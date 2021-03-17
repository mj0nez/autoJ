# auotJ - ROI measurement in an image set
Copyright (C) 2021  mj0nez<br>Licensed under [GPL-3.0 License](LICENSE.md) 

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

On start the user is asked for a directory containing the image series as well
as optional arguments like file types or key words for filtering. After that
the first image is opened and a ROI has to be selected before the measurement
is taken via a user dialog. This process is repeated for n measurements,
defined in the first dialog window and all filter matching images.
Jython implementation for Fiji / ImageJ.

----------

## Requirements:

**DEPENDENCIES**

ImageJ 1.39r or later, because of the dependency of built-in WaitForUserDialog:
https://imagejdocu.tudor.lu/plugin/utilities/wait_for_user/start#usage_in_a_plugin

Other dependencies weren't tested. The development was done with ImageJ
1.53c. It's recommended to use the same or a newer release, although the
latter may need adjustment in the future.

**FILE NAMES**

To measure something on each image of a set, the file names should follow a
ascending naming scheme and / or be composed of a prefix and some additional
information. Alternatively delete all keywords in the filter input and the
script works on all files in the selected folder.

If you want to measure preprocessed images and sometimes need to view the
original, check 'allow Originals'. Then an original is required for every
image in the directory. To avoid errors follow the above mentioned naming
scheme and use different prefix for images to measure and to compare
(originals).

----------
## Usage:

**EXECUTION**

Open Fiji / ImageJ , then open this file in the onboard Script Editor via
dialog option FILE > OPEN... or by pressing CTRL + O.
Now RUN the script and the first dialog window will open.
During a run, the kill option is blocked due the gui elements.
    To end the script execution click OK and then hold ESC to manually exit.

**DIALOG OPTIONS**

Paste a path to a directory with an image series or browse for your data.
By default the last path and user inputs are shown. To modify this
behaviour replace the header with global constants e.g., 

replace:    
```
# @ String(label='File types', value='tif;png') file_types
```
with:
```
file_types = 'tif;png'
```
To filter your files and measure only specific images of your directory add
search keys (based on the images file name) as optional argument. For more
than one key use ; as separator (s.a.).
By default this script takes two measurements per image. Users may take more
values by adjusting this dialog option.
The export checkbox is implemented for further development...
By pressing ok the script searches for matching images and starts the
procedure.

**MEASUREMENT**

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

**RESULTS**

The results of all measurements can be found in the ImageJ results
window. Users may export all values as a csv file.
An automatically export function is planned for further releases.



## Resources:

This script is mainly based on the template 'Wiki_Jython_Tutorial_3.py'
and the below mentioned resources.

imagej doc:
https://imagej.nih.gov/ij/developer/api/overview-summary.html

imagej macro language:
https://imagej.nih.gov/ij/developer/macro/macros.html

Fiji Scripting Tutorial:
https://syn.mrc-lmb.cam.ac.uk/acardona/fiji-tutorial/

----------

**AUTHORS COMMENT:**

Compared with the normal packing and import of python modules, the import of
self written Jython modules is a bit more complex. To keep it simple this
script consists of only one module and doesn't need any further
installations. Simply open and run the file with ImageJ.
Fur further information on Jython packaging see:
https://imagej.net/Jython_Scripting

During development dent mistakes have shown to be the greatest cause of
errors. Therefore check dents containing a combination of spaces and tabs and
unify the indent of error lines.
The onboard script editor of ImageJ is a rudimentary development environment,
but offers an automatically relevance control. Therefore development may be
done in your favourite IDE with execution in ImageJ, after reloading the latest
script version.

----------