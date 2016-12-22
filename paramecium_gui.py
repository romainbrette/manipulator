'''
A special GUI for Paramecium experiments
'''
from simple_manipulator import *
from Tkinter import *
from devices import *
import pickle
from serial import SerialException


class ManipulatorApplication(ManipulatorApplication):
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

        self.frame_microscope = MicroscopeFrame(self, unit=stage, nmemories=2)
        self.frame_microscope.grid(row=0, column=0, padx=5, pady=5, sticky=N)

        self.frame_manipulator = []
        i = 0
        for name, unit in zip(names, units):
            frame = ManipulatorFrame(self, text=name, unit=unit)
            frame.grid(row=0, column=i + 1, padx=5, pady=5)
            self.frame_manipulator.append(frame)
            i += 1

        Button(self, text='Go', command=self.go).grid(row = 1, column = 0, padx=5, pady=5)
        Button(self, text='Grip', command=self.grip).grid(row = 2, column = 0, padx=5, pady=5)
        Button(self, text='Ungrip', command=self.ungrip).grid(row = 3, column = 0, padx=5, pady=5)

        self.focus_set()
        self.bind("<Key>", self.key)

        self.load_configuration()

    def key(self, event):
        shift = 3
        if event.keysym == 'Left':
            self.synchronous_move(shift, 0)
        elif event.keysym == 'Right':
            self.synchronous_move(-shift, 0)
        elif event.keysym == 'Up':
            self.synchronous_move(0, shift)
        elif event.keysym == 'Down':
            self.synchronous_move(0, -shift)
        elif event.keysym == 'Next':
            self.synchronous_move(0, 0, shift)
        elif event.keysym == 'Prior':
            self.synchronous_move(0, 0, -shift)
        elif event.keysym == 'space':
            self.grip()
        elif event.keysym == 'Escape':
            self.ungrip()
        else:
            print "pressed", event.keycode, event.keysym

    def synchronous_move(self, dx=0, dy=0, dz=0):
        for frame in self.frame_manipulator:
            frame.unit.relative_move(dx, axis=0)
            frame.unit.relative_move(dy, axis=1)
            frame.unit.relative_move(dz, axis=2)

    def go(self): # synchronous go (not truly necessary)
        for frame in self.frame_manipulator:
            frame.unit.go()

    def grip(self): # 5 um grip
        for frame in self.frame_manipulator:
            frame.unit.dev.relative_move(-5., axis=0)

    def ungrip(self):
        for frame in self.frame_manipulator:
            frame.unit.dev.relative_move(5., axis=0)


if __name__ == '__main__':
    root = Tk()
    root.title('Paramecium manipulator')
    try:
        dev = LuigsNeumann_SM10()
    except SerialException:
        print "L&N SM-10 not found. Falling back on fake device."
        dev = FakeDevice()
    microscope = XYZUnit(dev, [7, 8, 9])
    unit = [XYZUnit(dev, [1, 2, 3]),
            XYZUnit(dev, [4, 5, 6])]
    virtual_unit = [VirtualXYZUnit(unit[i], microscope) for i in range(len(unit))]

    print "Device initialized"

    app = ManipulatorApplication(root, microscope, virtual_unit, ['Left','Right']).pack(side="top", fill="both", expand=True)

    root.mainloop()
