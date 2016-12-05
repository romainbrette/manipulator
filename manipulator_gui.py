'''
Software to control SM-10 micromanipulator controller

Tkinter:
http://apprendre-python.com/page-tkinter-interface-graphique-python-tutoriel
http://fsincere.free.fr/isn/python/cours_python_tkinter.php
'''
from Tkinter import *
import tkFileDialog
from devices import *

ndevices = 2
dev = LuigsNeumann_SM10()
microscope = VirtualDevice(dev, [7,8,9])
manip = [VirtualDevice(dev, [1,2,3]),
         VirtualDevice(dev, [4,5,6])]

window = Tk()
window.title('Manipulator')

device_name = ['Left manipulator','Right manipulator']

class DeviceFrame(LabelFrame):
    '''
    A named frame that displays device coordinates
    '''
    def __init__(self, master = None, cnf = {}, dev = None, **kw):
        LabelFrame.__init__(self, master, cnf, **kw)

        self.dev = dev # device
        self.coordinate = [0,0,0]
        self.coordinate_text = [StringVar(), StringVar(), StringVar()]
        self.refresh_coordinates()
        self.coordinate_label = [None, None, None]
        for j in range(3):
            self.coordinate_label[j] = Label(self, textvariable = self.coordinate_text[j])
            self.coordinate_label[j].pack()

    def refresh_coordinates(self):
        for i in range(3):
            self.coordinate[i] = self.dev.position(i)
            self.coordinate_text[i].set("{:7.1f}".format(self.coordinate[i]) + " um")
        self.after(100, DeviceFrame.refresh_coordinates, self)


frame_microscope = DeviceFrame(window, text = 'Microscope', dev = microscope)
frame_microscope.pack(side=LEFT, padx=10, pady=10)

frame_manipulator = []
for i in range(ndevices):
    frame_manipulator.append(DeviceFrame(window, text = device_name[i], dev = manip[i]))
    frame_manipulator[i].pack(side=LEFT, padx=10, pady=10)

OK=Button(window, text="OK", command=window.quit)
OK.pack()

microscope.move(0, 100)
microscope.move(1, -100)
microscope.move(2, 0)

window.mainloop()
