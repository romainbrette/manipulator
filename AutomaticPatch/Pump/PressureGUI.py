"""
A simple patch-clamp GUI

Pressures
"""
from Tkinter import *
from ob1 import *
# from FakeOB import *
from numpy import *
filename = 'pressure.txt'

verbose = True


class PressureApplication(Frame):
    """
    The main application.
    """
    def __init__(self, master, controller):
        """
        Parameters
        ----------
        master : parent window
        controller : the pressure controller
        """
        Frame.__init__(self, master)
        self.master = master

        self.controller = controller

        self.patcher = LabelFrame(self, text='Patcher')
        self.patcher.grid(row=0, column=0)
        Button(self.patcher, text='High pressure', command=self.high_pressure).pack()
        Button(self.patcher, text='Nearing', command=self.nearing).pack()
        Button(self.patcher, text='Seal', command=self.seal).pack()
        Button(self.patcher, text='Release', command=self.release).pack()
        Button(self.patcher, text='Break in', command=self.break_in).pack()
        self.pressure_label = Label(self.patcher, text='')
        self.pressure_label.pack()

        self.recorder = LabelFrame(self, text='Recorder')
        self.recorder.grid(row=0, column=1)
        self.button_text = StringVar('')
        Button(self.recorder, textvariable=self.button_text, command=self.record).pack()
        self.button_text.set('Record')
        self.record_label = Label(self.recorder, text='Not recording')
        self.record_label.pack()
        self.isrecording = False

        self.measurement = list()  # Could also be a numpy array

        # We start with 0 pressure
        self.pressure = 0.
        self.release()

    def update_pressure(self, pressure):
        self.pressure = pressure
        self.controller.set_pressure(self.pressure)
        self.pressure_label['text'] = 'Pressure: {}mbar'.format(self.pressure)

    def high_pressure(self):
        if verbose:
            print "High pressure"
        self.update_pressure(800)  # mBar (800-1000 in 2012 Kodandaramaiah paper)

    def nearing(self):
        if verbose:
            print "Nearing"
        self.update_pressure(25)  # mBar (25-30)

    def seal(self):
        # Sealing with small negative pressure
        if verbose:
            print "Sealing"
        self.update_pressure(-25)   # (from Desai)
        # -15 to -20 in Kodandaramaiah paper?

    def release(self):
        # Release the pressure
        if verbose:
            print "Releasing"
        self.update_pressure(0)
        # -15 to -20 in Kodandaramaiah paper?

    def break_in(self):
        # Breaks in with a ramp
        # Holst thesis: 0 to -345 mBar in 1.5 second
        # Desai: -150 mBar for 1 second; repeated attempts
        if verbose:
            print "Breaking in; release after 1 s"
        self.update_pressure(-150)
        self.master.after(1000, self.release)

    def record(self):
        self.isrecording = not self.isrecording
        self.button_text.set(['Record', 'Stop'][self.isrecording])
        if self.isrecording:
            # Here we start clocked recording using a timer - could be different depending on the interface
            self.master.after(50, self.sample)  # 20 Hz recording
        else:
            # Save to while when it's finished
            with open(filename, 'wt') as f:
                for i in self.measurement:
                    f.writelines('{}\n'.format(i))
            self.record_label['text'] = 'Not recording'

    def sample(self):
        if self.isrecording:
            pressure = self.controller.measure()
            self.record_label['text'] = 'Pressure: {:.2f}mbar'.format(pressure)
            print pressure
            self.measurement.append(pressure)
            self.master.after(50, self.sample)

if __name__ == '__main__':
    root = Tk()
    root.title('Patcher')

    controller = OB1()
    app = PressureApplication(root, controller).pack(side="top", fill="both", expand=True)
    root.mainloop()
