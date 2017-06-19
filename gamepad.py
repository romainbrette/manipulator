import threading
import time
from Tkinter import *
import ttk

import inputs
import numpy as np

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

class GamepadControl(Frame):
    def __init__(self, controller, axes, scale=(1, 1), master=None):
        Frame.__init__(self, master)
        self.master = master
        self.controller = controller
        self.axes = axes
        self.scale = scale
        self.abs_x = Label(self, text='force: 0')
        self.abs_x.pack()
        self.x = 0
        self.y = 0
        self.force = 0
        self.angle = 0
        self.abs_y = Label(self, text='angle: 0')
        self.abs_y.pack()

        gamepad = inputs.devices.gamepads[0]
        self.event_container = []
        reader = GamepadReader(self.event_container, gamepad)
        reader.start()
        self.after(10, self.update_labels)
        self.after(50, self.update_speed)

    def update_labels(self):
        for event in self.event_container:
            sign = -1 if event.state < 0 else 1
            if abs(event.state) < 4096:
                state = 0
            else:
                state = int(round((abs(event.state) - 4096)/ 3584.) * sign) * 2
            if event.code == 'ABS_X':
                self.x = event.state / 32768.0
            elif event.code == 'ABS_Y':
                self.y = event.state / 32768.0
            self.force = int(np.clip(np.round(np.clip(np.sqrt(self.x**2 + self.y**2) - 0.2, 0, 1) * 19), 0, 15))
            self.angle = np.arctan2(self.x, self.y)
            self.abs_x['text'] = 'force: {}'.format(self.force)
            self.abs_y['text'] = 'angle: {:.0f}'.format(self.angle*180/np.pi)
        self.event_container[:] = []
        self.after(10, self.update_labels)

    def update_speed(self):
        factor = 3
        if self.force != 0:
            speed = 16 if self.force >=8 else 8

            x = speed * np.sin(self.angle) * self.scale[0]
            y = speed * np.cos(self.angle) * self.scale[1]
            speed_x = np.argmin(abs(revolutions - abs(x)/12))
            speed_y = np.argmin(abs(revolutions - abs(y)/12))
            self.controller.set_slow_speed(self.axes[0], speed_x)
            self.controller.set_slow_speed(self.axes[1], speed_y)
            self.controller.relative_move_group([factor*x, factor*y], self.axes, fast=False)

        self.after(50, self.update_speed)

if __name__ == '__main__':
    root = Tk()
    dev = LuigsNeumann_SM10('COM3')
    GamepadControl(dev, axes=[7, 8], scale=[-1, 1], master=root).pack()
    root.mainloop()
