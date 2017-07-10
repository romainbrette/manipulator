'''
Puts droplets on a grid on the coverslip
'''

from Tkinter import *
from time import sleep

from numpy import pi, sin, cos
from serial import SerialException

from AutomaticPatch.Pressure_controller.pump_devices.OB1 import *
from devices import *


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

        # angle of the manipulator
        self.angle = 35./180*pi

        self.pump = OB1()

        Button(self, text="Reference", command=self.reference).pack()
        Button(self, text="Go", command=self.go).pack()
        Button(self, text="Droplet", command=self.droplet).pack()

        self.pump.set_pressure(30)

    def droplet(self):
        self.pump.set_pressure(100)
        sleep(.05)
        self.pump.set_pressure(30)

    def reference(self):
        '''
        Sets the reference point
        '''
        self.refx = self.unit.position(0)
        self.refz = self.unit.position(2)

    def go(self):
        '''
        Assumes the pipette is in place on the coverslip
        '''
        # Go up, move stage, go down

        x = self.unit.position(0)
        z = self.unit.position(2)

        # We calculate dx and dz for a 1 mm move on the coverslip
        '''
        dx = x-self.refx
        dz = z-self.refz
        '''
        dx = -1000/cos(self.angle)
        dz = dx*sin(self.angle)

        self.unit.set_single_step_distance(0, dx/8)
        self.unit.set_single_step_distance(1, 250)
        self.unit.set_single_step_distance(2, dz/8)
        #self.unit.absolute_move(z-1000,axis = 2) # I should put a flag until_still = True

        sign = 1
        for j in range(4):
            for i in range(4):
                if sign == 1:
                    self.unit.single_step(2, 8)
                    self.unit.wait_motor_stop(2)
                    self.droplet()
                    self.unit.single_step(0, 8)
                    #self.stage.absolute_move(x+2000, axis = 0)
                    self.unit.wait_motor_stop(0)
                else:
                    self.unit.single_step(0, -8)
                    self.unit.wait_motor_stop(0)
                    self.droplet()
                    self.unit.single_step(2, -8)
                    sleep(1)
                self.unit.wait_motor_stop(2)
            sign=-sign
            self.unit.single_step(2, 8)
            self.unit.wait_motor_stop(2)
            self.droplet()
            self.unit.single_step(1, 4)
            self.unit.wait_motor_stop(1)
            self.unit.single_step(2, -8)
            self.unit.wait_motor_stop(2)
            sleep(1)
        self.unit.single_step(2, 8)
        sleep(3)
        print "done"

        self.pump.set_pressure(0)

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
        dev.set_single_step_velocity(2, 15)
        dev.set_single_step_velocity(3, 15)
        dev.set_single_step_velocity(1, 15)

    print "Device initialized"

    app = ManipulatorApplication(root, microscope, unit).pack(side="top", fill="both", expand=True)

    try:
        root.mainloop()
    except SerialException:
        del(dev)
