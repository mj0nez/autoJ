# @ File(label='Choose a directory', style='directory') import_dir
# @ String(label='File types', value='tif;png') file_types
# @ String(label='Filter Images', value='GFP') filters_measure
# @ String(label='Filter Originals', value='GFP') filters_original
# @ Boolean(label='allow Originals', value=True) allow_orig
# @ Integer(label='Measurements / Image', value=2) measurements
# @ Boolean(label='Export Results', value=False) do_export

"""auotJ - ROI measurement in an image set

Jython implementation for Fiji / ImageJ.
On start the user is asked for a directory containing the image series as well
as optional arguments like file types or key words for filtering. After that
the first image is opened and a ROI has to be selected before the measurement
is taken via a user dialog. This process is repeated for n measurements,
defined in the first dialog window and all filter matching images.

----------

REQUIREMENTS:

ImageJ 1.39r or later, because of the dependency of built-in WaitForUserDialog:
https://imagejdocu.tudor.lu/plugin/utilities/wait_for_user/start#usage_in_a_plugin
Other dependencies weren't tested. The development was done with ImageJ
1.53c. It's recommended to use the same or a newer release, although the
latter may need adjustments in the future.

- FILE NAMES
To measure something on each image of a set, the file names should follow a
ascending naming scheme and / or be composed of a prefix and some additional
information. Alternatively delete all keywords in the filter input and the
script works on all files in the selected folder.

If you want to measure preprocessed images and sometimes need to view the
original, check 'allow Originals'. Then the script requires an original for
every image to measure. To avoid errors follow the above mentioned naming
scheme and use different prefix for images to measure and compare (originals).

----------

USAGE:

- EXECUTION

Open Fiji / ImageJ , then open this file in the onboard Script Editor via
dialog option FILE > OPEN... or by pressing CTRL + O.
Now RUN the script and the first dialog window will open.
During a run, the kill option is blocked due the gui elements.
    To end the script execution click OK and then hold ESC to manually exit.

- DIALOG OPTIONS
Paste a path to a directory with an image series or browse for your data.
By default the last path and user inputs are shown. To modify this
behaviour replace the header with global constants e.g.,
replace:    # @ String(label='File types', value='tif;png') file_types
with:       file_types = 'tif;png'
To filter your files and measure only specific images of your directory add
search keys (based on the images file name) as optional argument. For more
than one key use ; as separator (s.a.).
By default this script takes two measurements per image. Users may take more
values by adjusting this dialog option.
The export checkbox is implemented for further development...
By pressing ok the script searches for matching images and starts the
procedure.

- MEASUREMENT
On start the script opens the first image and a dialog option. Later is
used to take a measurement and advance. This script uses simple ui
settings, therefore users may arrange windows first.
    Note, that windows always open on the same monitor as ImageJ. After
    arranging the gui layout, it will maintain over different executions.
Before proceeding by clicking OK, select a region of interest (ROI) to
measure. The script asks for n measurements before proceeding to the next
image.
    If the image has no sufficient data, close it BEFORE advancing by
    pressing OK. Otherwise a measurement is taken even though no ROI has
    been selected (ROI is the whole image).
    To open a new image, advance mit OK till it's shown.
    For further study, skipped images can be found in the console output.
If a measurement failed and the image ist still open:
    Just delete the measurement from the results window, select a new ROI and
    MANUALLY measure with the dialog option ANALYZE > MEASURE or press CTRL + M.
    This procedure has has no effect on the script execution but allows
    corrections.
    If the last measurement failed and the script already proceeded, note the
    image number, delete the values from your results and repeat the
    measurements after the run.

- RESULTS
The results of all measurements can be found in the ImageJ results
window. Users may export all values as a csv file.
An automatically export function is planned for further releases.

----------

RESOURCES:

This script is mainly based on the template 'Wiki_Jython_Tutorial_3.py'
and the below mentioned resources.

imagej doc:
https://imagej.nih.gov/ij/developer/api/overview-summary.html

imagej macro language:
https://imagej.nih.gov/ij/developer/macro/macros.html

Fiji Scripting Tutorial:
https://syn.mrc-lmb.cam.ac.uk/acardona/fiji-tutorial/

----------

AUTHORS COMMENT:

During development dent mistakes have shown to be the greatest cause of
errors. Therefore check dents containing a combination of spaces and tabs and
unify the indent of error lines.
The onboard script editor of ImageJ is a rudimentary development environment,
but offers an automatically relevance control. Therefore development may be
done in your favourite IDE with execution in ImageJ, after reloading the latest
script version.
Compared with the normal packing and import of python modules, the import of
self written Jython modules is a bit more complex. To keep it simple this
script consists of only one module and doesn't need any further
installations. Simply open and run the file with ImageJ.
Fur further information on Jython packaging see:
https://imagej.net/Jython_Scripting

----------
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


def filter_directory(path, file_type=None, name_filter=None, recursive=False):
    """Creates a list of all criteria matching files in the given folder.

    :param path:        The path from were to open the images.
                        String and java.io.File are allowed.
    :param file_type:   Only accept files with the given extension
                        (default: None).
    :param name_filter: Only accept files that contain the given string
                        (default: None).
    :param recursive:   Process directories recursively
                        (default: False).
    """
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
    # If we don't want a recursive search, we can use os.listdir().
    if not recursive:
        for file_name in os.listdir(path):
            full_path = os.path.join(path, file_name)
            if os.path.isfile(full_path):
                if check_type(file_name):
                    if check_filter(file_name):
                        path_to_images.append(full_path)
    # For a recursive search os.walk() is used.
    else:
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


def measure_block():
    # save image name before user choice
    image_name = str(WM.getCurrentImage())
    # 1st macro call, to wait for user action and avoid accessing a closed image
    WaitForUserDialog("Proceed...?", "Select ROI and click 'OK'").show()
    img = WM.getCurrentImage()
    # print imp
    if img:
        IJ.run(img, "Measure", "")
    else:
        print('Skipped image:')
        print(image_name)


def print_console_notes():
    # display notes on usage to console
    line = "________________________________________________________________" \
           "_________________________________________________ "
    greet = "PLEASE NOTE:"
    execution = "\n-> Execution Kill is blocked. Click OK and then Hold ESC " \
                "to manually exit script...  <-"
    skip_img = "\nIf you wish to skip an image just close it and proceed with" \
               " 'OK' to the next one.\nIn this case no measurement is taken." \
               " If you proceed without closing, the whole image is measured. "
    back_to_img = "\nIn case you wish to return to it later:\nCopy the file " \
                  "name from the console, rerun the script and paste it into " \
                  "the filter dialog. "
    outputs = [line, greet, execution, skip_img, back_to_img, line]
    for o in outputs:
        print(o)


def open_image(file_path):
    # IJ.openImage() returns an ImagePlus object or None.
    imp = IJ.openImage(file_path)
    # An object equals True and None equals False.
    if imp:
        return imp
    else:
        return None


class ButtonClick(ActionListener):
    """Class which unique function is to handle the button clicks
    For accessibility this class is defined in the same file. It handles the
    onclick event of a simple java window, to open the original image of a
    preprocessed image to simplify access during execution.
    """
    # init properties
    original_path = None  # path to an image
    original_handle = None  # handle of an image
    opened = False  # boolean allows closing of original

    def set_original(self, orig):
        # saves handle of an image instance
        self.original_path = orig  # to pass arguments to actionPerformed
        self.opened = False  # to avoid closing a not show image

    def actionPerformed(self, event):
        # onclick action, implements abstract method 'actionPerformed' from
        # 'java.awt.event.ActionListener'
        self.original_handle = open_image(self.original_path)
        if not self.original_handle:
            print("Couldn't create an ImagePlus object from:",
                  str(self.original_path))
            return
        self.original_handle.show()  # open original image
        self.opened = True  # if true will be closed if script advances


def run_script():
    # This enables us to stop the script by just calling return.
    # replace original header with constant:
    do_recursive = True
    # # @ Boolean(label='Recursive search', value=True) do_recursive

    # Run the filter_directory() function using the Scripting Parameters.
    path_list_images = filter_directory(import_dir,
                                        split_string(file_types),
                                        split_string(filters_measure),
                                        do_recursive)

    path_list_originals = filter_directory(import_dir,
                                           split_string(file_types),
                                           split_string(filters_original),
                                           do_recursive)
    if not path_list_images or not path_list_originals:
        # exit script without matching path_list_images
        print('No matching path_list_images could be found. Please check input arguments'
              '\nScript was cancelled.')
        return

    # note on runtime exit
    print_console_notes()

    if allow_orig:
        # generate button to show corresponding original_path image_path
        # first generate java window frame
        frame = JFrame("Open Original Image", visible=True)
        frame.setSize(500, 125)
        # create button and onclick event s.a.
        button = JButton("Open Original")
        button_event = ButtonClick()
        button.addActionListener(button_event)
        # We associate the button objects to some instance of the ButtonClick class
        frame.getContentPane().add(button)
        frame.pack()

    # looping through matching path_list_images
    for image_path, original_path in zip(path_list_images, path_list_originals):
        # IJ.log(str(image_path )) # to log file names
        # open method used to open different extension image_path file
        image = open_image(image_path)
        if not image:
            print("Couldn't create an ImagePlus object from:", str(image_path))
            return
        image.show()
        # set name of original_path image_path in instance of action listener
        if allow_orig:
            button_event.set_original(original_path)
        # calls measure function and logs results
        # by adjusting the inner loop, more measurements per image_path are possible
        for i in range(measurements):
            # measure ROIs per image_path
            measure_block()
        # close image_path after n measurements
        image.close()
        if allow_orig and button_event.opened:
            button_event.original_handle.close()

    # post processing:
    if do_export:
        print("here comes the export")
    # close java window and end script with console message
    if allow_orig:
        frame.dispose()


if __name__ in ['__builtin__', '__main__']:
    run_script()
    print("\n...finished autoJ.py")
