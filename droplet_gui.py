'''
Puts droplets on a grid on the coverslip
'''

from Tkinter import *
from devices import *
from geometry import *
import pickle
from serial import SerialException
from numpy import array
from time import sleep

class ManipulatorApplication(Frame):
    '''
    The main application.
    '''
    def __init__(self, master, stage, unit):
        '''
        Parameters
        ----------
        master : parent window
        stage : the stage/microscope unit
        units : a list of XYZ virtual units (manipulators)
        names : names of the units
        '''
        Frame.__init__(self, master)

        self.stage = stage
        self.unit = unit

        Button(self, text="Go", command=self.go).pack()

    def go(self):
        '''
        Assumes the pipette is in place on the coverslip
        '''
        # Go up, move stage, go down

        z = self.unit.position(axis = 2)
        x = self.stage.position(axis = 0)
        self.unit.single_step_distance(2, 250)
        self.stage.single_step_distance(2, 250)
        #self.unit.absolute_move(z-1000,axis = 2) # I should put a flag until_still = True
        self.unit.single_step(2, -4)
        sleep(1)
        self.stage.single_step(0, 8)
        #self.stage.absolute_move(x+2000, axis = 0)
        sleep(1)
        #self.unit.absolute_move(z, axis = 2)
        self.unit.single_step(2, 4)
        sleep(1)
        print "done"

if __name__ == '__main__':
    root = Tk()
    root.title('Droplet generator')

    SM5 = False

    try:
        if SM5:
            dev = LuigsNeumann_SM5('COM3')
        else:
            dev = LuigsNeumann_SM10()
    except SerialException:
        print "L&N not found. Falling back on fake device."
        dev = FakeDevice()

    if SM5:
        microscope_Z = Leica('COM1')
        microscope = XYMicUnit(dev, microscope_Z, [7, 8])
        unit = XYZUnit(dev, [4, 5, 6])
    else:
        microscope = XYZUnit(dev, [7, 8, 9])
        unit = XYZUnit(dev, [1, 2, 3])

    print "Device initialized"

    app = ManipulatorApplication(root, microscope, unit).pack(side="top", fill="both", expand=True)

    try:
        root.mainloop()
    except SerialException:
        del(dev)
