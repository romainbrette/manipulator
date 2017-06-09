import threading
import time
from Tkinter import *
import ttk

import inputs

from devices.luigsneumann_SM10 import LuigsNeumann_SM10

revolutions = [0.000017,
               0.000040,
               0.000141,
               0.000260,
               0.001280,
               0.02630,
               0.05070,
               0.010200,
               0.025100,
               0.060100,
               0.173000,
               0.332000,
               0.498000,
               0.664000,  # TODO: Says 0.066400 in the docs...
               0.996000,
               1.328000]

class GamepadReader(threading.Thread):
    def __init__(self, event_container, gamepad):
        self.event_container = event_container
        self.gamepad = gamepad
        super(GamepadReader, self).__init__()

    def run(self):
        while True:
            event = self.gamepad.read()[0]
            if event.code in ['ABS_X', 'ABS_Y']:
                self.event_container.append(event)

class Application(Frame):
    def __init__(self, controller, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.controller = controller
        self.abs_x = Label(self, text='X: 0')
        self.abs_x.pack()
        self.speed_x = 0
        self.abs_y = Label(self, text='Y: 0')
        self.abs_y.pack()
        self.speed_y = 0

        gamepad = inputs.devices.gamepads[0]
        self.event_container = []
        reader = GamepadReader(self.event_container, gamepad)
        reader.start()
        self.after(10, self.update_labels)
        self.after(100, self.update_speed)

    def update_labels(self):
        for event in self.event_container:
            sign = -1 if event.state < 0 else 1
            if abs(event.state) < 4096:
                state = 0
            else:
                state = int(round((abs(event.state) - 4096)/ 1792.) * sign)
            if event.code == 'ABS_X':
                self.abs_x['text'] = 'X: {}'.format(state)
                self.speed_x = state
            elif event.code == 'ABS_Y':
                self.abs_y['text'] = 'Y: {}'.format(state)
                self.speed_y = state
        self.event_container[:] = []
        self.after(10, self.update_labels)

    def update_speed(self):
        factor = 1.5
        if self.speed_x != 0:
            self.controller.set_single_step_velocity(1, abs(self.speed_x))
            self.controller.set_single_step_distance(1, abs(self.speed_x)*revolutions[abs(self.speed_x)-1]*factor)
            step = 1 if self.speed_x > 0 else -1
            self.controller.single_step(1, step)
        else:
            self.controller.stop(1)
        if self.speed_y != 0:
            self.controller.set_single_step_velocity(2, abs(self.speed_y))
            self.controller.set_single_step_distance(2, abs(self.speed_y)*revolutions[abs(self.speed_y)-1]*factor)
            step = 1 if self.speed_x > 0 else -1
            self.controller.single_step(2, step)
        else:
            self.controller.stop(2)
        self.after(100, self.update_speed)

if __name__ == '__main__':
    root = Tk()
    dev = LuigsNeumann_SM10('COM3')
    Application(dev, master=root).pack()
    root.mainloop()
