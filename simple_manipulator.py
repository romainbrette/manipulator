'''
Simple manipulator GUI.

A simple program with no camera.
* Microscope: positions
* Manipulators: Go, calibrate (secondary)
   optionally: change pipette (but maybe not: just home, move up in z, back in X)
* No saving of configuration

Calibration is done in a separate program.


TODO:
* Safe movements: first on focal plane, then along X axis
* Configuration data should include device information.
* Error catching
* Refactoring: move virtualxyzunit into xyz unit
'''
from Tkinter import *
from devices import *
from geometry import *
import pickle
from serial import SerialException
from numpy import array

from os.path import expanduser
home = expanduser("~")
config_filename = home+'/config_manipulator.cfg'

__all__ = ['MicroscopeFrame', 'ManipulatorFrame', 'ManipulatorApplication']


class MicroscopeFrame(Frame):
    '''
    A frame for the stage positions.
    '''
    def __init__(self, master = None, unit = None, nmemories = 5, cnf = {}, **kw):
        '''
        Parameters
        ----------
        master : parent window
        unit : XYZ unit
        '''
        Frame.__init__(self, master, cnf, **kw)

        self.master = master
        self.unit = unit # XYZ unit

        Button(self, text='Move to plane', command=self.move_to_plane).pack()

    def move_to_plane(self):
        '''
        Moves the focus to the plane of interest.
        '''
        self.unit.absolute_move(self.plane.project(self.unit.position(), array([0.,0.,1.])))

class ManipulatorFrame(LabelFrame):
    '''
    A frame for a manipulator, showing virtual coordinates.
    '''
    def __init__(self, master = None, unit = None, cnf = {}, dev = None, **kw):
        LabelFrame.__init__(self, master, cnf, **kw)

        self.master = master
        self.unit = unit # XYZ unit

        Button(self, text="Go", command=self.go).pack()
        Button(self, text="Calibrate", command=self.calibrate).pack()

    def go(self):
        self.unit.go()

    def calibrate(self):
        self.unit.secondary_calibration()  # unless in calibration

class ManipulatorApplication(Frame):
    '''
    The main application.
    '''
    def __init__(self, master, stage, units, names):
        '''
        Parameters
        ----------
        master : parent window
        stage : the stage/microscope unit
        units : a list of XYZ virtual units (manipulators)
        names : names of the units
        '''
        Frame.__init__(self, master)

        self.frame_microscope = MicroscopeFrame(self, unit=stage)
        self.frame_microscope.grid(row=0, column=0, padx=5, pady=5, sticky=N)

        self.frame_manipulator = []
        i = 0
        for name, unit in zip(names, units):
            frame = ManipulatorFrame(self, text=name, unit=unit)
            frame.grid(row=0, column=i + 1, padx=5, pady=5)
            self.frame_manipulator.append(frame)
            i += 1

        self.load_configuration()

    def load_configuration(self):
        '''
        Load calibration
        '''
        cfg_all = pickle.load(open(config_filename, "rb"))
        for frame, cfg in zip(self.frame_manipulator, cfg_all['manipulator']):
            frame.unit.M = cfg['M']
            frame.unit.Minv = cfg['Minv']
            frame.unit.x0 = cfg['x0']
        self.frame_microscope.plane = cfg_all['microscope'].get('plane', None)

if __name__ == '__main__':
    root = Tk()
    root.title('Manipulator')

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
        unit = [XYZUnit(dev, [4, 5, 6]),
                XYZUnit(dev, [1, 2, 3])]
    else:
        microscope = XYZUnit(dev, [7, 8, 9])
        unit = [XYZUnit(dev, [1, 2, 3]),
                XYZUnit(dev, [4, 5, 6])]
    virtual_unit = [VirtualXYZUnit(unit[i], microscope) for i in range(len(unit))]

    print "Device initialized"

    app = ManipulatorApplication(root, microscope, virtual_unit, ['Left','Right']).pack(side="top", fill="both", expand=True)

    try:
        root.mainloop()
    except SerialException:
        del(dev)
