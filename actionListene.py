from fiji.util.gui import GenericDialogPlus
from java.awt.event import ActionListener
from javax.swing import JFrame, JButton, JOptionPane


class ButtonClic(ActionListener):
    '''Class which unique function is to handle the button clics'''
    prop = None

    def actionPerformed(self, event):
        # implement abstract method 'actionPerformed' from
        # 'java.awt.event.ActionListener'
        print(self, self.prop)

    def set_original(self, orig):
        self.prop = orig


frame = JFrame("Open Original Image", visible=True)
frame.setSize(500,125)
button = JButton("Open Original")
button_event = ButtonClic()
button_event.set_original(645665)

button.addActionListener(button_event)
# We associate the button objects to some instance of the ButtonClick class
frame.getContentPane().add(button)
frame.pack()
#frame.showDialog()
