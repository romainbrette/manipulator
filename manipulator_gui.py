'''
Software to control SM-10 micromanipulator controller

TODO:
* Group moves (in LN SM 10)
* Move up/down: continuous increase?
* Change pipette
* Safer moves
* Memories with editable names
'''
from Tkinter import *
from devices import *
from numpy import array, zeros
from numpy.linalg import LinAlgError
import pickle

class MemoryFrame(Frame):
    '''
    A frame for saving/load current position in memory
    '''
    def __init__(self, master=None, name = '', unit = None, cnf={}, dev=None, **kw):
        Frame.__init__(self, master, cnf, **kw)

        self.master = master
        self.unit = unit
        #self.name = StringVar(value = name)
        self.name = name
        Label(self, text = self.name).pack(side = LEFT)
        Button(self, text="Store", command=self.store).pack(side = LEFT)
        Button(self, text="Go", command=self.go).pack(side = LEFT)

    def store(self):
        self.unit.memory[self.name] = self.unit.position()
        self.master.master.display_status("Storing position '"+self.name+"'")

    def go(self):
        self.unit.absolute_move(self.unit.memory[self.name])
        self.master.master.display_status("Moving to position '" + self.name + "'")


class CoordinateFrame(Frame):
    '''
    A frame for displaying a coordinate and moving up/down
    '''
    def __init__(self, master=None, value = None, callback = None, cnf={}, dev=None, **kw):
        Frame.__init__(self, master, cnf, **kw)

        self.master = master
        self.callback = callback
        Label(self, textvariable=value, width = 8).pack(side = LEFT)
        Button(self, text='-', command=self.minus).pack(side=LEFT)
        Button(self, text='+', command=self.plus).pack(side=RIGHT)

    def minus(self):
        self.callback(-1)

    def plus(self):
        self.callback(1)


class UnitFrame(LabelFrame):
    '''
    A named frame that displays unit coordinates.

    TODO:
    * change the move command
    '''
    def __init__(self, master = None, unit = None, cnf = {}, dev = None, **kw):
        '''
        Parameters
        ----------
        master : parent window
        unit : XYZ unit
        '''
        LabelFrame.__init__(self, master, cnf, **kw)

        self.master = master
        self.unit = unit # XYZ unit
        self.coordinate = [0,0,0]
        self.coordinate_text = [StringVar(), StringVar(), StringVar()]
        self.refresh_coordinates()

        CoordinateFrame(self, value=self.coordinate_text[0], callback=lambda x: self.move(0, x)).pack()
        CoordinateFrame(self, value=self.coordinate_text[1], callback=lambda x: self.move(1, x)).pack()
        CoordinateFrame(self, value=self.coordinate_text[2], callback=lambda x: self.move(2, x)).pack()

    def refresh_coordinates(self):
        for i in range(3):
            self.coordinate[i] = self.unit.position(i)
            self.coordinate_text[i].set("{:7.1f}".format(self.coordinate[i]))

    def move(self, j, direction):
        #self.unit.absolute_move(float(self.coordinate_text[j].get()), axis = j)
        self.unit.relative_move(10*direction, axis = j)

class MicroscopeFrame(UnitFrame):
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
        UnitFrame.__init__(self, master, unit, cnf, **kw)

        MemoryFrame(self, name="Calibration", unit=unit).pack()
        MemoryFrame(self, name="Preparation", unit=unit).pack()

class ManipulatorFrame(UnitFrame):
    '''
    A frame for a manipulator, showing virtual coordinates.

    TODO:
    * Change pipette
    '''
    def __init__(self, master = None, unit = None, cnf = {}, dev = None, **kw):
        UnitFrame.__init__(self, master, unit, cnf, **kw)

        Button(self, text="Go", command=self.go).pack()
        Button(self, text="Tip centered", command=self.tip_centered).pack()
        Button(self, text="Change pipette", command=self.change_pipette).pack()
        Button(self, text="Calibrate", command=self.calibrate).pack()

        MemoryFrame(self, name = "Position 1", unit = unit).pack()
        MemoryFrame(self, name = "Position 2", unit = unit).pack()

        # Calibration data
        self.calibration_step = -1
        self.calibration_x = zeros((4, 3))
        self.calibration_y = zeros((4, 3))

    def go(self):
        self.master.display_status("Moving pipette to microscope position.")
        self.unit.go()

    def tip_centered(self):
        if self.calibration_step==-1:
            self.unit.secondary_calibration()  # unless in calibration
            self.master.display_status("Recalibrated.")
        else: # in calibration
            self.calibration_x[self.calibration_step] = self.unit.stage.position()
            self.calibration_y[self.calibration_step] = self.unit.dev.position()
            if self.calibration_step == 3: # Done
                self.master.display_status("Calibration done.")
                try:
                    self.unit.primary_calibration(self.calibration_x,self.calibration_y)
                    self.display_precision()
                except LinAlgError:
                    self.master.display_status("Calibration failed (redundant positions).")
                self.calibration_step = -1
                # Move microscope back to first position
                self.unit.stage.absolute_move(self.calibration_x[0])
                # Withdraw pipette
                self.unit.home()
                #self.unit.dev.absolute_move(self.calibration_y[0]) # move pipette
            else: # move unit by 500 um along one axis
                self.master.display_status("Step " + str(self.calibration_step+2) +
                                           "\nMove stage to center pipette tip and press 'Tip centered'.")
                self.unit.dev.relative_move(500., axis = self.calibration_step)
                self.calibration_step+=1

    def change_pipette(self):
        # Move microscope to calibration position
        self.unit.stage.absolute_move(self.unit.stage.memory['Calibration'])
        self.unit.home()
        # TODO: move pipette in view, click "go"
        self.master.display_status("Center pipette tip in microscope view and press 'Tip centered'.")
        # TODO: move pipette back
        # TODO: move microscope back

    def calibrate(self):
        if self.calibration_step == -1:
            # Withdraw pipette
            self.unit.home()
            # Move microscope to calibration position
            self.unit.stage.absolute_move(self.unit.stage.memory['Calibration'])
            self.master.display_status("Step "+str(self.calibration_step+2)+
                                       "\nCenter pipette tip in microscope view and press 'Tip centered'.")
            self.calibration_step = 0
        else:
            self.master.display_status("Calibration aborted.")
            self.calibration_step = -1

    def display_precision(self):
        '''
        Displays the relative precision of calibration along the 3 axes
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

        self.statusframe = LabelFrame(self, text='Status')
        self.statusframe.grid(row=1, column=0, columnspan=3, padx=5, pady=30, sticky=W + E)
        self.status = StringVar('')
        Label(self.statusframe, textvariable=self.status, justify=LEFT).pack(padx=5, pady=5)
        Button(self, text="STOP", command=self.stop).grid(row=2, column=1, padx=5, pady=5)

        # Load configuration file
        cfg = pickle.load(open("config.cfg", "rb"))
        x = cfg['x']
        y = cfg['y']
        self.frame_manipulator[0].unit.primary_calibration(x, y)

        welcome_text =\
"""Set-up:
1) Move the microscope to the position of interest and store in "Preparation" memory.
2) Move the microscope up by about 2 mm above the preparation and store in "Calibration" memory.
3) Click Change pipette or Calibrate.
"""
        self.display_status(welcome_text)

        self.after(1000, self.refresh)

    def display_status(self, text):
        self.status.set(text)

    def stop(self):
        self.frame_microscope.unit.stop()
        for frame in self.frame_manipulator:
            frame.unit.stop()

    def save_configuration(self):
        '''
        Save memories and calibration.
        '''
        microscope_cfg = {'memory' : self.frame_microscope.unit.memory}
        manipulator_cfg = []
        for frame in self.frame_manipulator:
            cfg = {'memory' : frame.unit.memory,
                   'M' : frame.unit.M,
                   'x0' : frame.unit.x0,
                   'Minv' : frame.unit.Minv }
            manipulator_cfg.append(cfg)
        cfg_all = {'manipulator' : manipulator_cfg,
                   'microscope' : microscope_cfg}

        pickle.dump(cfg_all, open("config.cfg", "wb"))

    def load_configuration(self):
        '''
        Load memories and calibration
        '''
        cfg_all = pickle.load(open("config.cfg", "rb"))
        self.frame_microscope.unit.memory = cfg_all['microscope']['memory']
        for frame, cfg in zip(self.frame_manipulator, cfg_all['manipulator']):
            frame.unit.memory = cfg['memory']
            frame.unit.M = cfg['M']
            frame.unit.Minv = cfg['Minv']
            frame.unit.x0 = cfg['x0']

    def refresh(self):
        '''
        Refresh unit positions every second.
        '''
        self.frame_microscope.refresh_coordinates()
        for i in range(len(self.frame_manipulator)):
            self.frame_manipulator[i].refresh_coordinates()

        self.after(1000, self.refresh)


if __name__ == '__main__':
    root = Tk()
    root.title('Manipulator')
    ndevices = 2
    # dev = LuigsNeumann_SM10()
    dev = Device()
    microscope = XYZUnit(dev, [7, 8, 9])
    unit = [XYZUnit(dev, [1, 2, 3]),
            XYZUnit(dev, [4, 5, 6])]
    virtual_unit = [VirtualXYZUnit(unit[i], microscope) for i in range(ndevices)]

    print "Device initialized"

    app = ManipulatorApplication(root, microscope, virtual_unit, ['Left','Right']).pack(side="top", fill="both", expand=True)
    root.mainloop()
