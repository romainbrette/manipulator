# coding=utf-8
import os
import threading
import time
from Tkinter import *

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
            if event.code in ['ABS_X', 'ABS_Y', 'ABS_Z', 'ABS_RZ']:
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
        self.left_z = 0
        self.right_z = 0
        self.force = 0
        self.angle = 0
        self.previous_speed = 0
        self.angle_label = Label(self, text='angle: -')
        self.angle_label.pack()
        self.file_entry = Entry(self)
        self.file_entry.pack()
        self.record_button = Button(self, text='Start recording', command=self.record)
        self.record_button.pack()
        self.recording = False
        self.record_file = None
        self.start_time = None
        self.speed_setting = [1, 3, 5]
        # Z axis uses slowest speed
        self.controller.set_single_step_factor_trackball(self.axes[2], self.speed_setting[1])
        gamepad = inputs.devices.gamepads[0]
        self.event_container = []
        reader = GamepadReader(self.event_container, gamepad)
        reader.start()
        self.after(10, self.update_labels)
        self.after(50, self.update_speed)

    def record(self):
        if self.recording:
            # stop recording
            self.record_file.close()
            self.record_file = None
            self.record_button['text'] = 'Start recording'
            self.recording = False
        else:
            # start recording
            filename = self.file_entry.get()
            if os.path.isfile(filename):
                print('File %s already exists, appending to the existing file' % filename)
                self.record_file = open(filename, 'a')
            else:
                self.record_file = open(filename, 'w')
                self.record_file.write('time,force,angle,z\n')
            self.start_time = time.time()
            self.record_button['text'] = 'Stop recording'
            self.recording = True

    def update_labels(self):
        for event in self.event_container:
            if event.code == 'ABS_X':
                self.x = event.state / 32768.0
            elif event.code == 'ABS_Y':
                self.y = event.state / 32768.0
            elif event.code == 'ABS_Z':
                self.left_z = event.state / 255.
            elif event.code == 'ABS_RZ':
                self.right_z = event.state / 255.
            # Classify deviation from center (i.e. movement speed) into four classes
            # No movement, slow movement, medium movement, fast movement
            self.force = np.clip(int(np.sqrt(self.x**2 + self.y**2) * 4), 0, 3)
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
        if self.force > 0:
            speed = self.speed_setting[self.force - 1]
            if self.previous_speed != speed:
                self.controller.set_single_step_factor_trackball(self.axes[0], speed)
                self.controller.set_single_step_factor_trackball(self.axes[1], speed)
                self.previous_speed = speed
            x = np.sin(self.angle) * self.scale[0]
            y = np.cos(self.angle) * self.scale[1]
            if abs(x) > .01:
                if x> 0:
                    self.controller.single_step_trackball(self.axes[0], 1)
                else:
                    self.controller.single_step_trackball(self.axes[0], -2)
            if abs(y) > .01:
                if y> 0:
                    self.controller.single_step_trackball(self.axes[1], 1)
                else:
                    self.controller.single_step_trackball(self.axes[1], -2)

        z = self.left_z - self.right_z
        if abs(z) > 0.25:
            z_step = 1 if z > 0 else -2
            self.controller.single_step_trackball(self.axes[2], z_step)
        else:
            z_step = 0

        if self.recording:
            now = time.time() - self.start_time
            angle = ((int(round(self.angle / (np.pi/4))) + 4 )% 8) -4
            self.record_file.write('%f,%d,%d,%d\n' % (now, self.force, angle, z_step))
        self.z = 0
        self.after(50, self.update_speed)

if __name__ == '__main__':
    root = Tk()
    dev = LuigsNeumann_SM10('COM3')
    GamepadControl(dev, axes=[7, 8, 9], scale=[-1, 1, 1], master=root).pack()
    root.mainloop()
