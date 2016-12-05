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
#dev = Device()
microscope = VirtualDevice(dev, [7,8,9])
manip = [VirtualDevice(dev, [1,2,3]),
         VirtualDevice(dev, [4,5,6])]

print "Device initialized"

window = Tk()
window.title('Manipulator')

device_name = ['Left','Right']

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
#frame_microscope.pack(side=LEFT, padx=10, pady=10)
frame_microscope.grid(row=1, column = 0, padx = 5, pady = 5)

frame_manipulator = []
frame_transformed = []
go_button = []
cancel_button = []
for i in range(ndevices):
    frame_manipulator.append(DeviceFrame(window, text = device_name[i], dev = manip[i]))
    frame_manipulator[i].grid(row=0, column = i+1, padx = 5, pady = 5) #pack(side=LEFT, padx=10, pady=10)
    #frame_transformed.append(DeviceFrame(window, text=device_name[i], dev=manip[i]))
    #frame_transformed[i].grid(row=1, column=i + 1, padx = 5, pady = 5)  # pack(side=LEFT, padx=10, pady=10)
    go_button = Button(window, text="Go", command=window.quit)
    go_button.grid(row = 2, column = i+1)
    cancel_button = Button(window, text="Cancel", command=window.quit)
    cancel_button.grid(row = 3, column = i+1)

status_text=StringVar(value = "Nothing's happening")
status = Label(window, textvariable = status_text)
status.grid(row = 4, column = 0, columnspan = 3, pady = 30)

OK_button = Button(window, text="OK", command=window.quit)
OK_button.grid(row = 5, column = 0, columnspan = 3, padx = 5, pady = 5)

microscope.move(0, 0)
microscope.move(1, 0)
microscope.move(2, 0)

window.mainloop()
