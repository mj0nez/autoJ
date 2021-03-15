from javax.swing import JFrame, JButton, JOptionPane
from ij import IJ, WindowManager as WM

def action_button(event):
    """ event: the ActionEvent that tells us about the button having been clicked. """
    print("action")

def getOptions():
    # gd = GenericDialog("Options")
    # gd.addStringField("name", "Untitled")
    # gd.addNumericField("alpha", 0.25, 2)  # show 2 decimals
    # gd.addCheckbox("optimize", True)
    # types = ["8-bit", "16-bit", "32-bit"]
    # gd.addChoice("output as", types, types[2])
    # gd.addSlider("scale", 1, 100, 100)
    # gd.showDialog()
    # #
    # if gd.wasCanceled():
    #     print
    #     "User canceled dialog!"
    #     return
    #     # Read out the options
    # name = gd.getNextString()
    # alpha = gd.getNextNumber()
    # optimize = gd.getNextBoolean()
    # output = gd.getNextChoice()
    # scale = gd.getNextNumber()
    # return name, alpha, optimize, output, scale  # a tuple with the parameters
    frame = JFrame("Open Original Image", visible=True)
    button = JButton("Open", actionPerformed=action_button)
    frame.getContentPane().add(button)
    frame.pack()

if __name__ in ['__builtin__', '__main__']:
    options = getOptions()