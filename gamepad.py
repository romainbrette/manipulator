# coding=utf-8
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
        self.force_label = Label(self, text='force: 0')
        self.force_label.pack()
        self.x = 0
        self.y = 0
        self.force = 0
        self.angle = 0
        self.speed_x = 0
        self.speed_y = 0
        self.angle_label = Label(self, text='angle: -')
        self.angle_label.pack()
        self.speed_setting = [12, 15]
        gamepad = inputs.devices.gamepads[0]
        self.event_container = []
        reader = GamepadReader(self.event_container, gamepad)
        reader.start()
        self.after(10, self.update_labels)
        self.after(50, self.update_speed)

    def update_labels(self):
        for event in self.event_container:
            if event.code == 'ABS_X':
                self.x = event.state / 32768.0
            elif event.code == 'ABS_Y':
                self.y = event.state / 32768.0
            # Classify deviation from center (i.e. movement speed) into three class
            # No movement, slow movement, fast movement
            self.force = np.clip(int(np.sqrt(self.x**2 + self.y**2) * 3), 0, 2)
            # Bin direction into 45° steps
            self.angle = np.round(np.arctan2(self.x, self.y) / (np.pi/4)) * np.pi/4
            self.force_label['text'] = 'force: {}'.format(self.force)
            if self.force > 0:
                self.angle_label['text'] = 'angle: {:.0f}'.format(self.angle * 180 / np.pi)
            else:
                self.angle_label['text'] = 'angle: -'
        self.event_container[:] = []
        self.after(10, self.update_labels)

    def update_speed(self):
        factor = 21
        if self.force > 0:
            speed = revolutions[self.speed_setting[self.force-1]]
            x = factor * speed * np.sin(self.angle) * self.scale[0]
            y = factor * speed * np.cos(self.angle) * self.scale[1]
            if abs(x) > 1:
                speed_x = self.speed_setting[self.force-1]
                if speed_x != self.speed_x:
                    self.controller.set_slow_speed(self.axes[0], speed_x)
                    self.speed_x = speed_x
            else:
                x = 0
            if abs(y) > 1:
                speed_y = self.speed_setting[self.force - 1]
                if speed_y != self.speed_y:
                    self.controller.set_slow_speed(self.axes[1], speed_y)
                    self.speed_y = speed_y
            else:
                y = 0
            self.controller.relative_move_group([x, y], self.axes, fast=False)

        self.after(50, self.update_speed)

if __name__ == '__main__':
    root = Tk()
    dev = LuigsNeumann_SM10('COM3')
    GamepadControl(dev, axes=[7, 8], scale=[-1, 1], master=root).pack()
    root.mainloop()
