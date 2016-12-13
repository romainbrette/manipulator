'''
Manual calibration of manipulators with no camera feed.

TODO:
* Save configuration: only update the configuration dictionary
* Precision seems incorrect.
'''
from Tkinter import *
from devices import *
from numpy import array, zeros
from numpy.linalg import LinAlgError
import pickle
from serial import SerialException
import time

from os.path import expanduser
home = expanduser("~")
config_filename = home+'/config_manipulator2.cfg'


class ManipulatorFrame(LabelFrame):
    '''
    A frame for a manipulator.
    '''
    def __init__(self, master = None, unit = None, cnf = {}, dev = None, **kw):
        LabelFrame.__init__(self, master, cnf, **kw)

        self.master = master
        self.unit = unit # XYZ unit

        Button(self, text="Go", command=self.go).pack()
        Button(self, text="Calibrate", command=self.calibrate).pack()

        # Calibration data
        self.calibration_step = -1
        self.calibration_x = zeros((4, 3))
        self.calibration_y = zeros((4, 3))

    def go(self):
        self.master.display_status("Moving pipette to microscope position.")
        self.unit.go()

    def calibrate(self):
        if self.calibration_step == -1:
            self.master.display_status("Step 1"+
                                       "\nCenter pipette tip in microscope view and press 'Calibrate'.")
            self.calibration_step = 0
        else:
            self.calibration_x[self.calibration_step] = self.unit.stage.position()
            self.calibration_y[self.calibration_step] = self.unit.dev.position()
            if self.calibration_step == 3: # Done
                self.master.display_status("Calibration done.")
                try:
                    self.unit.primary_calibration(self.calibration_x,self.calibration_y)
                    #self.display_precision()
                except LinAlgError:
                    self.master.display_status("Calibration failed (redundant positions).")
                self.calibration_step = -1
            else:
                axis_name = ['X', 'Y', 'Z']
                self.master.display_status("Step " + str(self.calibration_step+2) +
                                           "\nMove pipette along the "+axis_name[self.calibration_step]+"axis, move stage to center pipette tip and press 'Calibrate'.")
                self.calibration_step+=1

    def display_precision(self):
        '''
        Displays the relative precision of calibration along the 3 axes. Seems incorrect.
        '''
        x,y,z = self.unit.calibration_precision()
        self.master.display_status("Precision:\n"+
                                   "x : "+"{:3.3f}".format(x)+"\n"+
                                   "y : "+"{:3.3f}".format(y)+"\n"+
                                   "z : "+"{:3.3f}".format(z))

class ManipulatorApplication(Frame):
    '''
    The main application.
    '''
    def __init__(self, master, units, names):
        '''
        Parameters
        ----------
        master : parent window
        units : a list of XYZ virtual units (manipulators)
        names : names of the units
        '''
        Frame.__init__(self, master)

        self.stage = units[0].stage # Microscope and stage

        self.frame_manipulator = []
        i = 0
        for name, unit in zip(names, units):
            frame = ManipulatorFrame(self, text=name, unit=unit)
            frame.grid(row=0, column=i, padx=5, pady=5)
            self.frame_manipulator.append(frame)
            i += 1

        self.statusframe = LabelFrame(self, text='Status')
        self.statusframe.grid(row=1, column=0, columnspan=3, padx=5, pady=30, sticky=W + E)
        self.status = StringVar('')
        Label(self.statusframe, textvariable=self.status, justify=LEFT).pack(padx=5, pady=5)
        Button(self, text="Motor ranges", command=self.motor_ranges).grid(row=2, column=0, padx=5, pady=5)

        self.configuration = dict()
        self.load_configuration()

        self.motor_ranges_status = -1 # -1 means not doing the calibration

    def display_status(self, text):
        self.status.set(text)

    def save_configuration(self):
        '''
        Save calibration.
        '''
        for i,frame in enumerate(self.frame_manipulator):
            try:
                self.configuration['manipulator'][i]['M'] = frame.unit.M
                self.configuration['manipulator'][i]['x0'] = frame.unit.x0
                self.configuration['manipulator'][i]['Minv'] = frame.unit.Minv
            except KeyError: # not calibrated yet
                print "Manipulator",i,"is not calibrated yet"

        pickle.dump(self.configuration, open(config_filename, "wb"))

    def load_configuration(self):
        '''
        Load calibration
        '''
        try:
            self.configuration = pickle.load(open(config_filename, "rb"))
            for frame, cfg in zip(self.frame_manipulator, self.configuration['manipulator']):
                frame.unit.M = cfg['M']
                frame.unit.Minv = cfg['Minv']
                frame.unit.x0 = cfg['x0']
        except IOError:
            self.display_status("No configuration file.")
            # Initialization
            self.configuration = {'microscope' : dict(), 'manipulator' : [dict() for _ in self.frame_manipulator]}

    def minmax(self, p1, p2):
        '''
        Calculate min(p1.x, p2.x) for each XYZ coordinate,
        and max(p1.x, p2.x) for each XYZ coordinate.
        '''
        return array([min(p1[i], p2[i]) for i in range(len(p1))]),\
               array([max(p1[i], p2[i]) for i in range(len(p1))])

    def motor_ranges(self):
        '''
        Measure the range of all motors.
        '''
        if self.motor_ranges_status == -1:
            self.display_status("Move the stage and microscope to one corner and click 'Motor ranges'.")
            self.motor_ranges_status = 0
        elif self.motor_ranges_status == 0:
            self.x1 = self.stage.position()
            self.display_status("Move the stage and microscope to the opposite corner and click 'Motor ranges'.")
            self.motor_ranges_status = 1
        elif self.motor_ranges_status == 1:
            # Measure position and calculate min and max positions
            self.x2 = self.stage.position()
            self.stage.memory['min'], self.stage.memory['max'] = self.minmax(self.x1, self.x2)
            print self.minmax(self.x1, self.x2)
            # Next device
            self.display_status("Move manipulator 1 to one corner and click 'Motor ranges'.")
            self.motor_ranges_status = 2
        elif self.motor_ranges_status % 2 == 0: # first corner clicked
            manipulator = self.frame_manipulator[self.motor_ranges_status/2-1].unit.dev
            self.x1 = manipulator.position()
            self.display_status("Move manipulator "+ str(self.motor_ranges_status/2)+" to the opposite corner and click 'Motor ranges'.")
            self.motor_ranges_status+= 1
        elif self.motor_ranges_status % 2 == 1: # opposite corner clicked
            manipulator = self.frame_manipulator[self.motor_ranges_status/2-1].unit.dev
            self.x2 = manipulator.position()
            manipulator.memory['min'], manipulator.memory['max'] = self.minmax(self.x1,self.x2)
            print self.minmax(self.x1, self.x2)
            if self.motor_ranges_status/2<len(self.frame_manipulator):
                self.display_status("Move manipulator "+ str(self.motor_ranges_status/2+1)+" to the first corner and click 'Motor ranges'.")
                self.motor_ranges_status+= 1
            else: # Done
                self.display_status("Motor range calibration done.")
                self.motor_ranges_status = -1

    def destroy(self):
        self.save_configuration()


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

    app = ManipulatorApplication(root, virtual_unit, ['Left','Right']).pack(side="top", fill="both", expand=True)

    root.mainloop()
