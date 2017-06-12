from Tkinter import *
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
        self.pack()
        self.createwidgets()

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
                self.calibrate.config(state='normal', command=self.calibration)
                self.zero.config(state='normal')
                self.connection.config(state='disabled')
                self.disconnection.config(state='normal')
                self.after(10, self.show)
        pass

    def disconnect(self):
        del self.robot
        self.robot = None
        self.calibrate.config(command=None, state='disable')
        self.imgsave.config(state='disable', command=None)
        self.zero.config(state='disable')
        self.controllist['state'] = "readonly"
        self.armlist['state'] = 'readonly'
        self.connection.config(state='normal')
        self.disconnection.config(state='disabled')
        pass

    def calibration(self):

        calibrate = self.robot.calibrate()
        if calibrate:
            print 'Calibration succesfull.'
        else:
            print 'Calibration canceled.'
        pass

    def reset_pos(self):
        if self.robot:
            self.robot.go_to_zero()
        pass

    def show(self):
        if self.robot:
            self.robot.show()
            self.robot.enable_clic_position()
            self.after(10, self.show)

    def exit(self):
        del self.robot
        self.quit()

    def createwidgets(self):

        self.controllist = ttk.Combobox(self, state='readonly', values='SM5 SM10')
        self.controllist.grid(row=0, column=0, columnspan=2, padx=2, pady=2)

        self.armlist = ttk.Combobox(self, state='readonly', values='dev1 dev2')
        self.armlist.grid(row=1, column=0, columnspan=2, padx=2, pady=2)

        self.connection = Button(self, text='Connect', command=self.connect)
        self.connection.grid(row=2, column=0)

        self.disconnection = Button(self, text='Disconnect', command=self.disconnect, state='disable')
        self.disconnection.grid(row=2, column=1)

        self.calibrate = Button(self, text='Calibrate', state='disable')
        self.calibrate.grid(row=3, column=0)

        self.zero = Button(self, text='Go to zero', command=self.reset_pos, state='disable')
        self.zero.grid(row=3, column=1)

        self.imgsave = Button(self, text='Screenshot', state='disable')
        self.imgsave.grid(row=4, column=1)

        self.QUIT = Button(self, text='QUIT', fg='red', command=self.exit)
        self.QUIT.grid(row=4, column=0)

if __name__ == '__main__':
    root = Tk()
    app = Application(master=root)
    app.mainloop()
    root.destroy()
