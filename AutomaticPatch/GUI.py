'''
Simple GUI for the patch clamp robot
'''
from Tkinter import *
from tkMessageBox import *
import ttk
from PatchClampRobot import *


class Application(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)

        # State variables
        self.pause = 0
        self.calibrated = 0

        # Variables for manipulator, microscope
        self.robot = None
        self.controller = None
        self.arm = None
        self.continuous = False

        # GUI
        self.robot_box = LabelFrame(self, text='Connection')
        self.robot_box.grid(row=0, column=0, padx=5, pady=5)

        self.ask_controller = Label(self.robot_box, text='Controller: ')
        self.ask_controller.grid(row=0, column=0, padx=2, pady=2)

        self.controllist = ttk.Combobox(self.robot_box, state='readonly', values='SM5 SM10')
        self.controllist.grid(row=0, column=1, columnspan=2, padx=2, pady=2)

        self.ask_arm = Label(self.robot_box, text='Arm: ')
        self.ask_arm.grid(row=1, column=0, padx=2, pady=2)

        self.armlist = ttk.Combobox(self.robot_box, state='readonly', values='dev1 dev2')
        self.armlist.grid(row=1, column=1, columnspan=2, padx=2, pady=2)

        self.connection = Button(self.robot_box, text='Connect', command=self.connect, bg='green', fg='white')
        self.connection.grid(row=2, column=0, padx=2, pady=2)

        self.disconnection = Button(self.robot_box, text='Disconnect', command=self.disconnect, state='disable')
        self.disconnection.grid(row=2, column=1, padx=2, pady=2)

        self.calibrate_box = LabelFrame(self, text='Calibration')
        self.calibrate_box.grid(row=0, column=1, padx=2, pady=2)

        self.calibrate = Button(self.calibrate_box, text='Calibrate', state='disable')
        self.calibrate.grid(row=0, column=0, padx=2, pady=2)

        self.load_calibrate = Button(self.calibrate_box, text='Load calibration', state='disable')
        self.load_calibrate.grid(row=0, column=1, padx=2, pady=2)

        self.meter_box = LabelFrame(self, text='Resistance metering')
        self.meter_box.grid(row=1, column=1, padx=2, pady=2)

        self.continuous_meter = Checkbutton(self.meter_box, text='Continiuous metering',
                                            command=self.enable_continuous_meter,
                                            state='disable')
        self.continuous_meter.grid(row=0, column=0, padx=2, pady=2)

        self.res_window = Label(self.meter_box, text='Resistance: ')
        self.res_window.grid(row=1, column=0, padx=2, pady=2)

        self.res_value = Label(self.meter_box, text='0 Ohm')
        self.res_value.grid(row=1, column=1, padx=2, pady=2)

        self.misc = LabelFrame(self, text='misc')
        self.misc.grid(row=1, column=0, padx=2, pady=2)

        self.zero = Button(self.misc, text='Go to zero', command=self.reset_pos, state='disable')
        self.zero.grid(row=0, column=0, padx=2, pady=2)

        self.imgsave = Button(self.misc, text='Screenshot', state='disable')
        self.imgsave.grid(row=0, column=1, padx=2, pady=2)

        self.QUIT = Button(self, text='QUIT', bg='orange', fg='white', command=self.exit)
        self.QUIT.grid(row=2, column=0, padx=2, pady=2)

        self.pack()

    def connect(self):
        self.controller = self.controllist.get()
        self.arm = self.armlist.get()
        if not self.controller:
            print 'Please specify a controller.'
        else:
            if not self.arm:
                print 'Please specify a device for the arm.'
            else:
                self.robot = PatchClampRobot(self.controller, self.arm)
                self.controllist['state'] = 'disabled'
                self.armlist['state'] = 'disabled'
                self.imgsave.config(state='normal', command=self.robot.save_img)
                self.load_calibrate.config(state='normal', command=self.load_cali)
                self.calibrate.config(state='normal', command=self.calibration)
                self.zero.config(state='normal')
                self.connection.config(state='disabled')
                self.disconnection.config(state='normal')
                self.continuous_meter.config(state='normal')
        pass

    def disconnect(self):
        self.robot.stop()
        self.calibrate.config(command=None, state='disable')
        self.imgsave.config(state='disable', command=None)
        self.load_calibrate.config(state='disable', command=None)
        self.zero.config(state='disable')
        self.controllist['state'] = "readonly"
        self.armlist['state'] = 'readonly'
        self.connection.config(state='normal')
        self.disconnection.config(state='disabled')
        pass

    def calibration(self):
        if showinfo('Calibrating',
                    'Please put the tip of the pipette in focus and at the center of the image.'):

            if self.robot.calibrate():
                showinfo('Calibrating', 'Calibration succesfull.')
            else:
                showerror('Calibrating', 'Calibration canceled.')
            pass

    def load_cali(self):

        if showinfo('Loading calibration',
                    'Please put the tip of the pipette in focus and at the center of the image.'):
            if self.robot.load_calibration():
                self.robot.arm.set_to_zero([0, 1, 2])
                self.robot.microscope.set_to_zero([0, 1, 2])
            else:
                showerror('Loading calibration', 'The device has never been calibrated.')

    def reset_pos(self):
        if self.robot:
            self.robot.go_to_zero()
        pass

    def get_res(self):
        if self.robot:
            if self.continuous:
                val = str(self.robot.get_resistance())
                unit = (len(val)-3) // 3
                length = len(val) - 2 - unit*3
                if unit <= 0:
                    unit = ' Ohm'
                elif unit == 1:
                    unit = ' kOhm'
                elif unit == 2:
                    unit = ' MOhm'
                elif unit == 3:
                    unit = ' GOhm'
                elif unit == 4:
                    unit = ' TOhm'
                else:
                    unit = ' 1E{} Ohm'.format(unit*3)

                self.res_value['text'] = val[:length] + ',' + val[length:length+2] + unit
                self.after(10, self.get_res)
        pass

    def enable_continuous_meter(self):
        if self.robot:
            self.robot.set_continuous_res_meter(True)
            self.continuous = True
            self.continuous_meter.config(command=self.disable_continuous_meter)
            self.get_res()
        pass

    def disable_continuous_meter(self):
        if self.robot:
            self.robot.set_continuous_res_meter(False)
            self.continuous = False
            self.continuous_meter.config(command=self.enable_continuous_meter)

    def exit(self):
        if self.robot:
            self.robot.stop()
            del self.robot
        self.quit()


if __name__ == '__main__':
    root = Tk()
    root.title('Automatic Patch Clamp')
    root.resizable(width=False, height=False)
    app = Application(master=root)
    root.protocol("WM_DELETE_WINDOW", app.exit)
    app.mainloop()
    try:
        root.destroy()
    except TclError:
        # Already destroyed
        pass
