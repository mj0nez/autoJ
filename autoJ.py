# @ File(label='Choose a directory', style='directory') import_dir
# @ String(label='File types', value='tif;png') file_types
# @ String(label='Filter Images', value='GFP') filters_measure
# @ String(label='Filter Originals', value='GFP') filters_original
# @ Boolean(label='allow Originals', value=True) allow_orig
# @ Integer(label='Measurements / Image', value=2) measurements
# @ Boolean(label='Export Results', value=False) do_export

"""autoJ - ROI measurement in an image set

A Jython based script to automate ROI measurement for a set of images with Fiji.
Users choose a directory containing the images as well as optional arguments
like file types or key words for filtering. After that the first image is opened
and a the user selects a ROI to measure and the script proceeds with an user
dialog. This process is repeated for n measurements, defined in the first
window and all filter matching images.

If you are working with preprocessed files, a further dialog option enables
users to automatically open a corresponding original during measurements,
presuming that both sets follow the same naming scheme.

----------

Please refer to the README to check requirements, instructions and usage
options.

----------

## License & copyright

Copyright (C) 2021  mj0nez <br>Licensed under [GPL-3.0 License
](LICENSE.md)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see https://www.gnu.org/licenses/lgpl-3.0.
"""

# TODO:
#  - add csv export via results:
#  https://syn.mrc-lmb.cam.ac.uk/acardona/fiji-tutorial/#measurements-results-table

import os
# java imports
from java.io import File
from javax.swing import JFrame, JButton, JOptionPane
from java.awt.event import ActionListener
# ImageJ imports
from ij import IJ, WindowManager as WM
from ij.gui import GenericDialog, WaitForUserDialog


def filter_directory(path, file_type=None, name_filter=None):
    """Creates a list of all criteria matching files in the given folder.

    :param path:        The path from were to open the images.
                        String and java.io.File are allowed.
    :param file_type:   Only accept files with the given extension
                        (default: None).
    :param name_filter: Only accept files that contain the given string
                        (default: None).
    """
    # string and strip user inputs
    file_type = split_string(file_type)
    name_filter = split_string(name_filter)

    # Converting a File object to a string.
    if isinstance(path, File):
        path = path.getAbsolutePath()

    def check_type(string):
        """This function is used to check the file type.
        It is possible to use a single string or a list/tuple of strings as
        filter. This function can access the variables of the surrounding
        function.
        :param string: The filename to perform the check on.
        """
        if file_type:
            # The first branch is used if file_type is a list or a tuple.
            if isinstance(file_type, (list, tuple)):
                for file_type_ in file_type:
                    if string.endswith(file_type_):
                        # Exit the function with True.
                        return True
                    else:
                        # Next iteration of the for loop.
                        continue
            # The second branch is used if file_type is a string.
            elif isinstance(file_type, string):
                if string.endswith(file_type):
                    return True
                else:
                    return False
            return False
        # Accept all files if file_type is None.
        else:
            return True

    def check_filter(string):
        """This function is used to check for a given filter.
        It is possible to use a single string or a list/tuple of strings as filter.
        This function can access the variables of the surrounding function.
        :param string: The filename to perform the filtering on.
        """
        if name_filter:
            # The first branch is used if name_filter is a list or a tuple.
            if isinstance(name_filter, (list, tuple)):
                for name_filter_ in name_filter:
                    if name_filter_ in string:
                        # Exit the function with True.
                        return True
                    else:
                        # Next iteration of the for loop.
                        continue
            # The second branch is used if name_filter is a string.
            elif isinstance(name_filter, string):
                if name_filter in string:
                    return True
                else:
                    return False
            return False
        else:
            # Accept all files if name_filter is None.
            return True

    # We collect all files to open in a list.
    path_to_images = []
    # Replacing some abbreviations (e.g. $HOME on Linux).
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)

    # os.walk() is iterable.
    # Each iteration of the for loop processes a different directory.
    # the first return value represents the current directory.
    # The second return value is a list of included directories.
    # The third return value is a list of included files.
    for directory, dir_names, file_names in os.walk(path):
        # We are only interested in files.
        for file_name in file_names:
            # The list contains only the file names.
            # The full path needs to be reconstructed.
            full_path = os.path.join(directory, file_name)
            # Both checks are performed to filter the files.
            if check_type(file_name):
                if check_filter(file_name):
                    # Add the file to the list of images to open.
                    path_to_images.append(full_path)
    return path_to_images


def split_string(input_string):
    """Split a string to a list and strip it
    :param input_string: A string that contains semicolons as separators.
    """
    string_splitted = input_string.split(';')
    # Remove whitespace at the beginning and end of each string
    strings_striped = [string.strip() for string in string_splitted]
    return strings_striped


def measure_block(measure_i):
    # save image reference before user choice
    img_ref = WM.getCurrentImage()

    # plugin call holds loop until user continues
    WaitForUserDialog("Proceed...?",
                      "Select ROI or skip image by closing it and click"
                      "OK'").show()
    if WM.getCurrentImage():
        # only if image is open
        IJ.run(img_ref, "Measure", "")
    elif img_ref:
        print('Skipped measure %s of: %s' % (str(measure_i+1), img_ref))
    else:
        print('Skipped measure %s of: s.a.' % str(measure_i + 1))


def open_image(file_path):
    # IJ.openImage() returns an ImagePlus object or None.
    imp = IJ.openImage(file_path)
    # An object equals True and None equals False.
    return imp if imp else None


class ButtonClick(ActionListener):
    """Class which unique function is to handle the button clicks
    For accessibility this class is defined in the same file. It handles the
    onclick event of a simple java window, to open the original image of a
    preprocessed image to simplify access during execution.
    """
    # init properties
    original_path   = None      # path to an image
    original_handle = None      # handle of an image
    opened          = False     # boolean allows closing of original

    def set_original(self, orig):
        """saves handle of an image instance

        :param orig:    handle of image: ImagePlus object
        :return:        None
        """
        self.original_path  = orig      # to pass arguments to actionPerformed
        self.opened         = False     # to avoid closing a not show image

    def actionPerformed(self, event):
        """Implementation of custom on-click event
        onclick action, implements abstract method 'actionPerformed' from
        java.awt.event.ActionListener'

        :param event:   argument of super method
        :return:        None
        """
        # opens only on image instance
        if self.opened:
            return

        self.original_handle = open_image(self.original_path)
        if not self.original_handle:
            print("Couldn't create an ImagePlus object from:",
                  str(self.original_path))
            return

        self.original_handle.show()
        self.opened = True  # if opened, will be closed if script advances


def print_console_notes():
    """Display notes on usage to console
    """
    line        = "_"*114
    greet       = "PLEASE NOTE:"
    execution   = "-> Execution Kill is blocked. Click OK and then Hold ESC" \
                  " to manually exit script...  <-"
    skip_img    = "If you wish to skip an image just close it and proceed " \
                  "with 'OK' to the next one.\nIn this case no measurement is" \
                  " taken. If you proceed without closing, the whole image is" \
                  " measured. "
    back_to_img = "In case you wish to return to it later:\nCopy the file " \
                  "name from the console, rerun the script and paste it into " \
                  "the filter dialog. "
    print('\n\n'.join(
                [line,
                 greet, execution, skip_img, back_to_img,
                 line]))


def print_filter_error(file_types, filters):
    """Prints custom error massage for filter

    :param file_types:  user input
    :param filters:     user input
    :return:
    """
    print('No matches for [%s] and [%s] in directory.'
          '\nPlease check input arguments.'
          % (file_types, filters))


def run_script():
    """ Main procedure of autoJ

    :return: boolean    True if successful, False if execution failed
    """

    # replaced original user dialog in header with constant:
    do_recursive = True
    # # @ Boolean(label='Recursive search', value=True) do_recursive

    # filter directory with user inputs from dialog in file header
    path_list_images = filter_directory(import_dir,
                                        file_types,
                                        filters_measure)
    # exit without matching images
    if not path_list_images:
        print_filter_error(file_types,
                           filters_measure)
        return False

    # do the same for originals
    if allow_orig:
        path_list_originals = filter_directory(import_dir,
                                               file_types,
                                               filters_original)
        if not path_list_originals:
            print_filter_error(file_types,
                               filters_original)
            return False

        # Generate user dialog to allow opening of originals
        frame = JFrame("Open Original Image",
                       visible=True, size=(500, 125))
        button = JButton("Open Original")
        button_event = ButtonClick()
        button.addActionListener(button_event)
        frame.getContentPane().add(button)
        frame.pack()
    else:
        # has no effect but to avoid referencing before assignment
        path_list_originals = path_list_images

    print_console_notes()

    # looping through matching files in path_lists
    for image_path, original_path in zip(path_list_images, path_list_originals):

        image = open_image(image_path)

        if not image:
            print('Could not create an ImagePlus object from: %s'
                  % str(image_path))
            return False

        image.show()    # for ROI selection

        if allow_orig:
            button_event.set_original(original_path)  # allows opening

        for i in range(measurements):
            measure_block(i)    # measure ROIs per image

        # close images after measurements
        image.close()
        if allow_orig and button_event.opened:
            button_event.original_handle.close()

    # Post processing:
    if do_export:
        print('here comes the export')
    if allow_orig:
        frame.dispose()  # close additional java window

    return True


if __name__ in ['__builtin__', '__main__']:
    val = run_script()
    if val:
        print('\n...finished autoJ.')
    else:
        print('\n...Script was cancelled.')
