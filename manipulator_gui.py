'''
Software to control SM-10 micromanipulator controller

TODO:
* Make a list of technical issues (camera handling, serial port etc)
* wait_until_still in SM10
* Safe last calibration point, to make safe movements (for z? or x)
* Precision does not seem correct
* Test group moves (in LN SM 10)
* Change pipette
    move pipette in axis, but withdrawn
* Safer moves
* Check motor bounds
* Add a scale bar
* Memories with editable names

Automatic calibration:
* Autofocus algorithm
    blur measure (variance) + scipy.optimize?
    xu et al 2011
    std dev normalized by mean
    get the z axis moving slowly; scan and measure variance;
    go to best point; fine tune
    Alternatively, use template match as focus function
'''
from Tkinter import *
from devices import *
from vision import *
from numpy import array, zeros, eye, dot
from numpy.linalg import LinAlgError, inv
import pickle
from serial import SerialException
import time

# For the camera
import cv2
from PIL import Image, ImageTk

from os.path import expanduser
home = expanduser("~")
config_filename = home+'/config_manipulator.cfg'

class CameraFrame(Toplevel):
    def __init__(self, master=None, cnf={}, dev=None, **kw):
        Toplevel.__init__(self, master, cnf, **kw)
        self.main = Label(self)
        self.main.bind("<Button-1>",self.click)
        self.main.pack()
        #width, height = 800, 600
        self.cap = cv2.VideoCapture(0)
        #self.cap.set(3, width)
        #self.cap.set(4, height)
        self.width = int(self.cap.get(3))
        self.height = int(self.cap.get(4))
        self.show_frame()

    def set_microscope(self, microscope):
        self.microscope = microscope

    def show_frame(self):
        if self.cap.isOpened():
            _, frame = self.cap.read()
            width, height = self.width, self.height
            # Center cross
            cv2.line(frame, (width / 2, height / 2 - 10), (width / 2, height / 2 + 10), (0, 0, 255))
            cv2.line(frame, (width / 2 - 10, height / 2), (width / 2 + 10, height / 2), (0, 0, 255))
            # Top left
            cv2.line(frame, (width / 3, height / 3 - 10), (width / 3, height / 3 + 10), (0, 0, 255))
            cv2.line(frame, (width / 3 - 10, height / 3), (width / 3 + 10, height / 3), (0, 0, 255))
            # Top right
            cv2.line(frame, (2*width / 3, height / 3 - 10), (2*width / 3, height / 3 + 10), (0, 0, 255))
            cv2.line(frame, (2*width / 3 - 10, height / 3), (2*width / 3 + 10, height / 3), (0, 0, 255))
            # Bottom left
            cv2.line(frame, (width / 3, 2*height / 3 - 10), (width / 3, 2*height / 3 + 10), (0, 0, 255))
            cv2.line(frame, (width / 3 - 10, 2*height / 3), (width / 3 + 10, 2*height / 3), (0, 0, 255))

            #frame = cv2.flip(frame, 1)
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            imgtk = ImageTk.PhotoImage(image=Image.fromarray(cv2image))
            self.main.imgtk = imgtk
            self.main.configure(image=self.main.imgtk)
            self.main.after(100, self.show_frame)

    def click(self, e):
        self.microscope.click(e.x, e.y)

    def autofocus(self):
        '''
        Autofocus algorithm.
        Ideally, use Xu et al. 2011, Robust Automatic Focus Algorithm for Low Contrast Images Using a New Contrast Measure

        Here we simply use normalized standard deviation of the image as focus function, and global search
        (or Fibonacci search or other; eg from scipy.optimize).
        '''
        print "Autofocus (in development)"
        timeout = 30. # Time out
        # Do this in show_frame()?
        # Capture 20 images
        img = []
        self.microscope.unit.relative_move(-10., axis=2)  # 1 um
        for i in range(20):
            _, frame = self.cap.read()
            img.append(frame)
            self.microscope.unit.relative_move(1., axis = 2) # 1 um
        pickle.dump(img, open('pipette_stack.img', "wb"))

    def destroy(self):
        self.cap.release()
        Toplevel.destroy(self)

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

        Button(self, text="Calibrate", command=self.calibrate).pack()
        Button(self, text="Autofocus", command=self.master.camera.autofocus).pack()
        MemoryFrame(self, name="Calibration", unit=unit).pack()
        MemoryFrame(self, name="Preparation", unit=unit).pack()

        # Calibration variables
        self.calibrate_step = -1
        self.x = zeros((3,2)) # we ignore the z dimension
        width, height = self.master.camera.width, self.master.camera.height
        self.y = zeros((3,2))
        self.y[0] = (width/3,height/3)
        self.y[1] = (2*width / 3, height / 3)
        self.y[2] = (width / 3, 2*height / 3)
        self.center = array([width / 2, height / 2])
        self.M = eye(2)
        self.Minv = eye(2)
        self.x0 = zeros(2)

    def click(self,xs,ys):
        if self.calibrate_step == -1:
            y = array([xs,ys]) # Camera position
            x = dot(self.M,y)+self.x0
            # Move manipulator 1
            x3D = self.unit.position()
            x3D[:2]+= x
            self.master.frame_manipulator[0].unit.absolute_move(x3D)
        elif self.calibrate_step == 0:
            self.x[0] = self.unit.position()[:2]
            self.y[0] = (xs, ys)
            self.master.display_status("Place point of interest in top right corner with the stage and click on it.")
            self.calibrate_step = 1
        elif self.calibrate_step == 1:
            self.x[1] = self.unit.position()[:2]
            self.y[1] = (xs, ys)
            self.master.display_status("Place point of interest in bottom left corner with the stage and click on it.")
            self.calibrate_step = 2
        else:  # Done
            self.x[2] = self.unit.position()[:2]
            self.y[2] = (xs, ys)
            self.master.display_status("Calibration done.")
            self.calculate_calibration()
            self.calibrate_step = -1

    def calibrate(self):
        if self.calibrate_step == -1:
            self.master.display_status("Place point of interest in top left corner with the stage and click on it.")
            self.calibrate_step = 0

    def calculate_calibration(self):
        dx = self.x.T
        dx = dx[:,1:] - dx[:,0:-1] # we calculate shifts relative to first position
        dy = self.y.T
        dy = dy[:, 1:] - dy[:, 0:-1]
        self.M = -dot(dx, inv(dy))
        self.Minv=inv(self.M)
        # Clicking on the center means no movement
        self.x0 = -dot(self.M, self.center)


class ManipulatorFrame(UnitFrame):
    '''
    A frame for a manipulator, showing virtual coordinates.

    TODO:
    * Change pipette
    '''
    def __init__(self, master = None, unit = None, cnf = {}, dev = None, **kw):
        UnitFrame.__init__(self, master, unit, cnf, **kw)

        Button(self, text="Go", command=self.go).pack()
        Button(self, text="Confirm position", command=self.confirm_position).pack()
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

    def confirm_position(self):
        if self.calibration_step==-1:
            self.unit.secondary_calibration()  # unless in calibration
            self.master.display_status("Recalibrated.")
        elif self.calibration_step==0:
            self.unit.save_home()
            self.master.display_status("Step 2"+
                                       "\nCenter pipette tip in microscope view and press 'Confirm position'.")
            self.calibration_step = 1
        else: # in calibration
            self.calibration_x[self.calibration_step-1] = self.unit.stage.position()
            self.calibration_y[self.calibration_step-1] = self.unit.dev.position()
            if self.calibration_step == 4: # Done
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
            else: # move unit by 500 um along one axis
                axis_name = ['X', 'Y', 'Z']
                self.master.display_status("Step " + str(self.calibration_step+2) +
                                           "\nMove pipette along the "+axis_name[self.calibration_step-1]+"axis, move stage to center pipette tip and press 'Confirm position'.")
                #self.unit.dev.relative_move(500., axis = self.calibration_step-1)
                self.calibration_step+=1

    def change_pipette(self):
        # Move microscope to calibration position
        self.unit.stage.absolute_move(self.unit.stage.memory['Calibration'])
        # Withdraw pipette
        self.unit.home()
        # TODO: move pipette in view, click "go"
        self.master.display_status("Center pipette tip in microscope view and press 'Confirm position'.")
        # TODO: move pipette back
        # TODO: move microscope back

    def calibrate(self):
        if self.calibration_step == -1:
            # Move microscope to calibration position
            self.unit.stage.absolute_move(self.unit.stage.memory['Calibration'])
            # Ask user to withdraw pipette
            self.master.display_status("Step 1"+
                                       "\nWithdraw the pipette and click 'Confirm position'.")
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

        self.camera = CameraFrame(master)
        self.camera.wm_title("Camera")

        self.frame_microscope = MicroscopeFrame(self, text='Microscope', unit=stage)
        self.frame_microscope.grid(row=0, column=0, padx=5, pady=5, sticky=N)

        self.camera.set_microscope(self.frame_microscope)

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
        Button(self, text="Motor ranges", command=self.motor_ranges).grid(row=2, column=0, padx=5, pady=5)
        Button(self, text="TEST", command=self.test).grid(row=2, column=2, padx=5, pady=5)

        self.load_configuration()

        welcome_text =\
"""Set-up:
1) Move the microscope to the position of interest and store in "Preparation" memory.
2) Move the microscope up by about 2 mm above the preparation and store in "Calibration" memory.
3) Click Change pipette or Calibrate.
"""
        self.display_status(welcome_text)

        self.motor_ranges_status = -1 # -1 means not doing the calibration

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
        microscope_cfg = {'memory' : self.frame_microscope.unit.memory,
                          'M' : self.frame_microscope.M,
                          'Minv' : self.frame_microscope.Minv,
                          'x0' : self.frame_microscope.x0}
        manipulator_cfg = []
        for frame in self.frame_manipulator:
            cfg = {'memory' : frame.unit.memory,
                   "dev.memory" : frame.unit.dev.memory,
                   'M' : frame.unit.M,
                   'x0' : frame.unit.x0,
                   'Minv' : frame.unit.Minv }
            manipulator_cfg.append(cfg)
        motor_cfg = {}
        cfg_all = {'manipulator' : manipulator_cfg,
                   'microscope' : microscope_cfg}

        pickle.dump(cfg_all, open(config_filename, "wb"))

    def load_configuration(self):
        '''
        Load memories and calibration
        '''
        try:
            cfg_all = pickle.load(open(config_filename, "rb"))
            self.frame_microscope.unit.memory = cfg_all['microscope']['memory']
            try:
                self.frame_microscope.M = cfg_all['microscope']['M']
                self.frame_microscope.Minv = cfg_all['microscope']['Minv']
                self.frame_microscope.x0 = cfg_all['microscope']['x0']
            except KeyError: # not yet updated
                pass
            for frame, cfg in zip(self.frame_manipulator, cfg_all['manipulator']):
                frame.unit.memory = cfg['memory']
                try:
                    frame.unit.dev.memory = cfg['dev.memory']
                except KeyError:
                    pass # not yet updated
                frame.unit.M = cfg['M']
                frame.unit.Minv = cfg['Minv']
                frame.unit.x0 = cfg['x0']
                frame.unit.is_calibrated = True
        except IOError:
            self.display_status("No configuration file.")
            time.sleep(1)

    def refresh(self):
        '''
        Refresh unit positions every second.
        '''
        self.frame_microscope.refresh_coordinates()
        for i in range(len(self.frame_manipulator)):
            self.frame_manipulator[i].refresh_coordinates()

        self.after(1000, self.refresh)

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
            self.x1 = self.frame_microscope.unit.position()
            self.display_status("Move the stage and microscope to the opposite corner and click 'Motor ranges'.")
            self.motor_ranges_status = 1
        elif self.motor_ranges_status == 1:
            # Measure position and calculate min and max positions
            self.x2 = self.frame_microscope.unit.position()
            self.frame_microscope.unit.memory['min'], self.frame_microscope.unit.memory['max'] = self.minmax(self.x1, self.x2)
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

    def test(self):
        '''
        We use this to test development functions.
        '''
        pass

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

    app = ManipulatorApplication(root, microscope, virtual_unit, ['Left','Right']).pack(side="top", fill="both", expand=True)

    root.mainloop()
