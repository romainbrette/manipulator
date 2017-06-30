"""
Records pressure during an experiment with the OB1
"""
from Tkinter import *
from os.path import expanduser
from numpy import *
from pump_devices import *

home = expanduser("~")
filename = home+'/pressure.txt'


class RecorderApplication(Frame):
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
        self.button_text = StringVar('')
        Button(self, textvariable=self.button_text, command=self.record).pack()
        self.button_text.set('Record')
        self.pressure_label = Label(self, text='Not recording')
        self.pressure_label.pack()
        self.isrecording = False

        self.measurement = list()  # Could also be a numpy array

    def record(self):
        self.isrecording = not self.isrecording
        self.button_text.set(['Record', 'Stop'][self.isrecording])
        if self.isrecording:
            # Here we start clocked recording using a timer - could be different depending on the interface
            self.master.after(50, self.sample)  # 20 Hz recording
        else:
            # Save to while when it's finished
            savetxt(filename, array(self.measurement))
            self.pressure_label['text'] = 'Not recording'

    def sample(self):
        if self.isrecording:
            pressure = self.controller.measure()
            self.pressure_label['text'] = 'Pressure: {:.2f}mbar'.format(pressure)
            print pressure
            self.measurement.append(pressure)
            self.master.after(50, self.sample)

if __name__ == '__main__':
    root = Tk()
    root.title('Pressure recorder')
    controller = OB1()
    app = RecorderApplication(root, controller).pack(side="top", fill="both", expand=True)

    root.mainloop()
