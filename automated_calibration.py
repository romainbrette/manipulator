'''
Automated calibration of manipulators using computer vision.
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
config_filename = home+'/config_manipulator_automated.cfg'

class CameraFrame(Toplevel):
    def __init__(self, master=None, cnf={}, dev=None, **kw):
        Toplevel.__init__(self, master, cnf, **kw)
        self.main = Label(self)
        self.main.pack()
        self.cap = cv2.VideoCapture(0)
        self.width = int(self.cap.get(3))
        self.height = int(self.cap.get(4))
        self.main.bind("<Button-1>",self.click_left)
        self.main.bind("<Button-2>",self.click_right)
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

            #frame = cv2.flip(frame, 1)
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            imgtk = ImageTk.PhotoImage(image=Image.fromarray(cv2image))
            self.main.imgtk = imgtk
            self.main.configure(image=self.main.imgtk)
            self.main.after(100, self.show_frame)

    def click_left(self, e):
        self.microscope.click(e.x, e.y, button = 1)

    def click_right(self, e):
        self.microscope.click(e.x, e.y, button = 2)

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
            self.microscope.unit.wait_until_still(axis = 2 )
        pickle.dump(img, open('pipette_stack.img', "wb"))

    def destroy(self):
        self.cap.release()
        Toplevel.destroy(self)


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

        Button(self, text="Calibrate", command=self.calibrate).pack()
        Button(self, text="Autofocus", command=self.master.camera.autofocus).pack()

        # Calibration variables
        self.calibrate_step = -1
        self.x = zeros((3,2)) # we ignore the z dimension
        width, height = self.master.camera.width, self.master.camera.height
        self.y = zeros((3,2))
        self.center = array([width / 2, height / 2])
        self.M = eye(2)
        self.Minv = eye(2)
        self.x0 = zeros(2)

    def click(self,xs,ys, button = None):
        y = array([xs,ys]) # Camera position
        x = dot(self.M,y)+self.x0
        # Move manipulator 1
        x3D = self.unit.position()
        x3D[:2]+= x
        print button
        self.master.frame_manipulator[button-1].unit.absolute_move(x3D)

    def calibrate(self): # Automatic calibration
        width, height = self.master.camera.width, self.master.camera.height
        self.x[0] = self.unit.position()[:2]
        self.y[0] = self.center
        _, template = self.master.camera.cap.read()
        cv2.imwrite('pipette1.jpg', template)
        # Extract a small template in the center
        template = template[height*3/8:height*5/8,width*3/8:width*5/8]
        # Move X axis
        self.unit.relative_move(50., axis = 0) # 50 um
        self.unit.wait_until_still(axis = 0)
        # Template matching
        _, img = self.master.camera.cap.read()
        self.x[1] = self.unit.position()[:2]
        x,y = find_template(img, template)[:2]
        self.y[1] = [x+width/8, y+height/8]
        cv2.imwrite('pipette2.jpg', img)
        # Move Y axis
        self.unit.relative_move(50., axis=1)  # 50 um
        self.unit.wait_until_still(axis=1)
        # Template matching
        _, img = self.master.camera.cap.read()
        self.x[2] = self.unit.position()[:2]
        x, y = find_template(img, template)[:2]
        self.y[2] = [x + width / 8, y + height / 8]
        cv2.imwrite('pipette3.jpg', img)
        print self.y[1],self.y[2]
        self.master.display_status("Calibration done.")
        self.calculate_calibration()

    def calculate_calibration(self):
        dx = self.x.T
        dx = dx[:,1:] - dx[:,0:-1] # we calculate shifts relative to first position
        dy = self.y.T
        dy = dy[:, 1:] - dy[:, 0:-1]
        self.M = -dot(dx, inv(dy))
        self.Minv=inv(self.M)
        # Clicking on the center means no movement
        self.x0 = -dot(self.M, self.center)


class ManipulatorFrame(LabelFrame):
    '''
    A frame for a manipulator, showing virtual coordinates.
    '''
    def __init__(self, master = None, unit = None, cnf = {}, dev = None, **kw):
        LabelFrame.__init__(self, master, cnf, **kw)

        self.master = master
        self.unit = unit # XYZ unit

        Button(self, text="Calibrate", command=self.calibrate).pack()

        # Calibration data
        self.calibration_step = -1
        self.calibration_x = zeros((4, 3))
        self.calibration_y = zeros((4, 3))

    def calibrate(self):
        if self.calibration_step == -1:
            # Ask user to withdraw pipette
            self.master.display_status("Step 1"+
                                       "\nWithdraw the pipette and click 'Calibrate'.")
            self.calibration_step = 0
        elif self.calibration_step == 0:
            self.master.display_status("Step 2" +
                                       "\nCenter pipette tip in microscope view and press 'Calibrate'.")
            self.calibration_step = 1
        else:  # in calibration
            self.calibration_x[self.calibration_step - 1] = self.unit.stage.position()
            self.calibration_y[self.calibration_step - 1] = self.unit.dev.position()
            if self.calibration_step == 4:  # Done
                self.master.display_status("Calibration done.")
                try:
                    self.unit.primary_calibration(self.calibration_x, self.calibration_y)
                    self.display_precision()
                except LinAlgError:
                    self.master.display_status("Calibration failed (redundant positions).")
                self.calibration_step = -1
            else:  # move unit by 500 um along one axis
                axis_name = ['X', 'Y', 'Z']
                self.master.display_status("Step " + str(self.calibration_step + 2) +
                                           "\nMove pipette along the " + axis_name[
                                               self.calibration_step - 1] + "axis, move stage to center pipette tip and press 'Calibrate'.")
                self.calibration_step += 1

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
        Button(self, text="Motor ranges", command=self.motor_ranges).grid(row=2, column=0, padx=5, pady=5)

        self.motor_ranges_status = -1 # -1 means not doing the calibration

    def display_status(self, text):
        self.status.set(text)

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

    def destroy(self):
        self.save_configuration()


if __name__ == '__main__':
    root = Tk()
    root.title('Automatic calibration')
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
