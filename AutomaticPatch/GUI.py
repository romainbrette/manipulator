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

        # GUI
        self.QUIT = None
        self.disconnection = None
        self.connection = None
        self.controllist = None
        self.armlist = None
        self.calibrate = None
        self.imgsave = None
        self.zero = None
        self.load_calibrate = None
        self.res_window = None
        self.res_value = None
        self.continuous_meter = None
        self.pack()
        self.create_widgets()

    def connect(self):
        self.controller = self.controllist.get()
        self.arm = self.armlist.get()
        if not self.controller:
            print 'Please specify a controller.'
        else:
            if not self.arm:
                print 'Please specify a device for the arm.'
            else:
                self.controllist['state'] = 'disabled'
                self.armlist['state'] = 'disabled'
                self.robot = PatchClampRobot(self.controller, self.arm)
                self.imgsave.config(state='normal', command=self.robot.save_img)
                self.load_calibrate.config(state='normal', command=self.robot.load_calibration)
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
            calibrate = self.robot.calibrate()

            if calibrate:
                print 'Calibration succesfull.'
            else:
                print 'Calibration canceled.'
            pass

    def load_cali(self):
        if self.robot.load_calibration():
            if showinfo('Loading calibration',
                        'Please put the tip of the pipette in focus and at the center of the image.'):
                self.robot.arm.set_to_zero([0, 1, 2])
                self.robot.microscope.set_to_zero([0, 1, 2])

    def reset_pos(self):
        if self.robot:
            self.robot.go_to_zero()
        pass

    def get_res(self):
        if self.robot:
            val = self.robot.get_resistance()
            unit = (len(val)-1) // 3
            length = len(val) - unit*3
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

            self.res_value['text'] = text[:length] + ',' + text[length:length+2] + unit
            self.after(10, self.get_res)
        pass

    def enable_continuous_meter(self):
        if self.robot:
            self.robot.set_continious_res_meter(True)
            self.continuous_meter.config(command=self.disable_continuous_meter, text='Continiuous metering Off')
            self.get_res()
        pass

    def disable_continuous_meter(self):
        if self.robot:
            self.robot.set_continious_res_meter(False)

    def exit(self):
        if self.robot:
            self.robot.stop()
            del self.robot
        self.quit()

    def create_widgets(self):

        self.controllist = ttk.Combobox(self, state='readonly', values='SM5 SM10')
        self.controllist.grid(row=0, column=0, columnspan=2, padx=2, pady=2)

        self.armlist = ttk.Combobox(self, state='readonly', values='dev1 dev2')
        self.armlist.grid(row=1, column=0, columnspan=2, padx=2, pady=2)

        self.connection = Button(self, text='Connect', command=self.connect)
        self.connection.grid(row=2, column=0)

        self.disconnection = Button(self, text='Disconnect', command=self.disconnect, state='disable')
        self.disconnection.grid(row=2, column=1)

        self.continuous_meter = Button(self, text='Continiuous metering On', command=self.enable_continuous_meter,
                                       state='disable')
        self.continuous_meter.grid(row=3, column=0)

        self.res_window = Label(self, text='Resistance: ')
        self.res_window.grid(row=4, column=0)

        self.res_value = Label(self, text='0 Ohm')
        self.res_window.grid(row=4, column=1)

        self.calibrate = Button(self, text='Calibrate', state='disable')
        self.calibrate.grid(row=5, column=0)

        self.load_calibrate = Button(self, text='Load calibration', state='disable')
        self.load_calibrate.grid(row=5, column=1)

        self.zero = Button(self, text='Go to zero', command=self.reset_pos, state='disable')
        self.zero.grid(row=6, column=0)

        self.imgsave = Button(self, text='Screenshot', state='disable')
        self.imgsave.grid(row=6, column=1)

        self.QUIT = Button(self, text='QUIT', fg='red', command=self.exit)
        self.QUIT.grid(row=7, column=0)

if __name__ == '__main__':
    root = Tk()
    app = Application(master=root)
    app.mainloop()
    root.destroy()
