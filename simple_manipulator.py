'''
Simple manipulator GUI.

A simple program with no camera.
* Microscope: positions
* Manipulators: Go, calibrate (secondary)
   optionally: change pipette (but maybe not: just home, move up in z, back in X)
* No saving of configuration

Calibration is done in a separate program.


TODO:
* Configuration data should include device information.
* Error catching
'''
from Tkinter import *
from devices import *
from numpy import array, zeros, eye, dot
from numpy.linalg import LinAlgError, inv
import pickle
from serial import SerialException
import time

from os.path import expanduser
home = expanduser("~")
config_filename = home+'/config_manipulator.cfg'

class MemoryFrame(Frame):
    '''
    A frame for saving/load current position in memory

    TODO: merge this with the microscope frame?
    '''
    def __init__(self, master=None, name = '', unit = None, cnf={}, dev=None, **kw):
        Frame.__init__(self, master, cnf, **kw)

        self.unit = unit
        self.name = StringVar(value = name)
        Entry(self, textvariable = self.name).pack(side = LEFT)
        Button(self, text="Store", command=self.store).pack(side = LEFT)
        Button(self, text="Go", command=self.go).pack(side = LEFT)

    def store(self):
        self.unit.memory[self.name.get()] = self.unit.position()

    def go(self):
        self.unit.absolute_move(self.unit.memory[self.name.get()])

class MicroscopeFrame(LabelFrame):
    '''
    A frame for the microscope and stage.
    '''
    def __init__(self, master = None, unit = None, cnf = {}, **kw):
        '''
        Parameters
        ----------
        master : parent window
        unit : XYZ unit
        '''
        LabelFrame.__init__(self, master, cnf, **kw)

        self.master = master
        self.unit = unit # XYZ unit

        for i in range(5):
            MemoryFrame(self, name="Position "+str(i+1), unit=unit).pack()

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

        self.frame_microscope = MicroscopeFrame(self, text='Microscope', unit=stage)
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
            frame.unit.is_calibrated = True

if __name__ == '__main__':
    root = Tk()
    root.title('Manipulator')
    ndevices = 2
    try:
        dev = LuigsNeumann_SM10()
    except SerialException:
        print "L&N SM-10 not found. Falling back on fake device."
        dev = FakeDevice()
    microscope = XYZUnit(dev, [7, 8, 9])
    unit = [XYZUnit(dev, [1, 2, 3]),
            XYZUnit(dev, [4, 5, 6])]
    virtual_unit = [VirtualXYZUnit(unit[i], microscope) for i in range(ndevices)]

    print "Device initialized"

    app = ManipulatorApplication(root, microscope, virtual_unit, ['Left','Right']).pack(side="top", fill="both", expand=True)

    root.mainloop()
