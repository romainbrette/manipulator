from Tkinter import *
from tkMessageBox import *
from ScrolledText import *
import ttk
from PatchClampRobot import *


class PatchClampGUI(Frame):
    """
    Simple GUI for the patch clamp robot.
    Controls:
        conect/disconnect robot (controller, arm, camera, amplifier and pump to be specified)
        Launch auto calibration
        Load previous calibration
        Set position to Zero
        Positionning pipette when left clicking on camera window
        Patch (and clamp if enable) at given position by right clicking on camera window
        Enable/disable clamp when right clicking
        Clamping
        Enable/disable pipette following the camera
        Enable/disable resistance metering
        Check pipette resistance for patch
    """

    def __init__(self, master=None):
        Frame.__init__(self, master)

        # State variables
        self.pause = 0
        self.calibrated = 0

        # Variables for manipulator, microscope
        self.robot = None
        self.controller = None
        self.arm = None
        self.camera = None
        self.amplifier = None
        self.pump = None
        self.continuous = IntVar()
        self.follow = IntVar()

        # GUI

        # Connection to robot
        self.robot_box = LabelFrame(self,
                                    text='Connection')
        self.robot_box.grid(row=0, column=0, padx=5, pady=5)

        # Controller
        self.ask_controller = Label(self.robot_box,
                                    text='Controller: ')
        self.ask_controller.grid(row=0, column=0, padx=2, pady=2)

        self.controllist = ttk.Combobox(self.robot_box,
                                        state='readonly',
                                        values='SM5 SM10')
        self.controllist.grid(row=0, column=1, columnspan=2, padx=2, pady=2)

        # Arm
        self.ask_arm = Label(self.robot_box,
                             text='Arm: ')
        self.ask_arm.grid(row=1, column=0, padx=2, pady=2)

        self.armlist = ttk.Combobox(self.robot_box,
                                    state='readonly',
                                    values='dev1 dev2')
        self.armlist.grid(row=1, column=1, columnspan=2, padx=2, pady=2)

        # Camera
        self.ask_camera = Label(self.robot_box,
                                text='Camera: ')
        self.ask_camera.grid(row=2, column=0, padx=2, pady=2)

        self.camlist = ttk.Combobox(self.robot_box,
                                    state='readonly',
                                    values='Hamamatsu Lumenera')
        self.camlist.grid(row=2, column=1, columnspan=2, padx=2, pady=2)

        # Amplifier
        self.ask_amp = Label(self.robot_box,
                             text='Amplifier: ')
        self.ask_amp.grid(row=3, column=0, padx=2, pady=2)

        self.amplist = ttk.Combobox(self.robot_box,
                                    state='readonly',
                                    values='FakeAmplifier Multiclamp')
        self.amplist.grid(row=3, column=1, columnspan=2, padx=2, pady=2)

        # Pump for pressure control
        self.ask_pump = Label(self.robot_box,
                              text='Pump: ')
        self.ask_pump.grid(row=4, column=0, padx=2, pady=2)

        self.pumplist = ttk.Combobox(self.robot_box,
                                     state='readonly',
                                     values='FakePump OB1')
        self.pumplist.grid(row=4, column=1, columnspan=2, padx=2, pady=2)

        # Connection button
        self.connection = Button(self.robot_box,
                                 text='Connect',
                                 command=self.connect,
                                 bg='green', fg='white')
        self.connection.grid(row=5, column=0, padx=2, pady=2)

        # disconnection button
        self.disconnection = Button(self.robot_box,
                                    text='Disconnect',
                                    command=self.disconnect,
                                    state='disable')
        self.disconnection.grid(row=5, column=1, padx=2, pady=2)

        # Auto calibration
        self.calibrate_box = LabelFrame(self,
                                        text='Calibration')
        self.calibrate_box.grid(row=0, column=1, padx=2, pady=2)

        # Begin calibration button
        self.calibrate = Button(self.calibrate_box,
                                text='Calibrate',
                                command=self.calibration,
                                state='disable')
        self.calibrate.grid(row=0, column=0, padx=2, pady=2)

        # Load the previous calibration button
        self.load_calibrate = Button(self.calibrate_box,
                                     text='Load calibration',
                                     command=self.load_cali,
                                     state='disable')
        self.load_calibrate.grid(row=0, column=1, padx=2, pady=2)

        # Control of amplifier
        self.meter_box = LabelFrame(self,
                                    text='Resistance metering')
        self.meter_box.grid(row=1, column=1, padx=2, pady=2)

        # Selection of meter: potential or resistance
        self.chosen_meter = IntVar()
        self.choose_resistance = Radiobutton(self.meter_box,
                                             text='Resistance metering',
                                             variable=self.chosen_meter,
                                             value=1)
        self.choose_resistance.grid(row=0, column=0, padx=2, pady=2)

        self.choose_potential = Radiobutton(self.meter_box,
                                            text='Potential metering',
                                            variable=self.chosen_meter,
                                            value=2)
        self.choose_potential.select()
        self.choose_potential.grid(row=0, column=1, padx=2, pady=2)

        # display resistance
        self.res_window = Label(self.meter_box,
                                text='Resistance: ')
        self.res_window.grid(row=1, column=0, padx=2, pady=2)

        self.res_value = Label(self.meter_box,
                               text='0 Ohm')
        self.res_value.grid(row=1, column=1, padx=2, pady=2)

        self.potential_window = Label(self.meter_box,
                                      text='Potential')
        self.potential_window.grid(row=2, column=0, padx=2, pady=2)

        self.potential_value = Label(self.meter_box,
                                     text='0 V')
        self.potential_value.grid(row=2, column=1, padx=2, pady=2)

        # Check the resistance of the pipette for patching button

        # continuous resistance metering on/off
        self.continuous_meter = Checkbutton(self.meter_box,
                                            text='Continiuous metering',
                                            variable=self.continuous,
                                            command=self.switch_continuous_meter,
                                            state='disable')
        self.continuous_meter.grid(row=3, column=0, padx=2, pady=2)

        self.check_pipette_resistance = Button(self.meter_box,
                                               text='Check pipette',
                                               command=self.init_patch_clamp,
                                               state='disable')
        self.check_pipette_resistance.grid(row=3, column=1, padx=2, pady=2)

        # Other controls
        self.misc = LabelFrame(self,
                               text='misc')
        self.misc.grid(row=1, column=0, padx=2, pady=2)

        # reset postion
        self.zero = Button(self.misc,
                           text='Go to zero',
                           command=self.reset_pos,
                           state='disable')
        self.zero.grid(row=0, column=0, padx=2, pady=2)

        # Screenshot
        self.imgsave = Button(self.misc,
                              text='Screenshot',
                              state='disable')
        self.imgsave.grid(row=0, column=1, padx=2, pady=2)

        # Clamp button
        self.clamp = Button(self.misc, text='Clamp', state='disable')
        self.clamp.grid(row=1, column=0, padx=2, pady=2)

        # Clamp when right click on/off
        self.clamp_switch = Checkbutton(self.misc,
                                        text='clamp when clicking',
                                        command=self.enable_clamp,
                                        state='disable')
        self.clamp_switch.grid(row=1, column=1, padx=2, pady=2)

        # Pipette follow camera on/off
        self.switch_follow = Checkbutton(self.misc,
                                         text='Following',
                                         command=self.following,
                                         variable=self.follow,
                                         state='disable')
        self.switch_follow.grid(row=2, column=0, padx=2, pady=2)

        # Messages zone
        self.text_zone = ScrolledText(master=self, width=50, height=5, state='disabled')
        self.text_zone.grid(row=2, column=0, columnspan=3)

        # Quit button
        self.QUIT = Button(self,
                           text='QUIT',
                           bg='orange',
                           fg='white',
                           command=self.exit)
        self.QUIT.grid(row=3, column=0, padx=2, pady=2)

        self.message = ''

        self.pack()

    def connect(self):
        """
        Connect to the robot
        """
        # Devices to connect to
        self.controller = self.controllist.get()
        self.arm = self.armlist.get()
        self.amplifier = self.amplist.get()
        self.pump = self.pumplist.get()
        self.camera = self.camlist.get()

        # Checking primordial devices have been specified: controller, arm and camera
        if not self.controller:
            showerror('Connection error', 'Please specify a controller.')
        elif not self.arm:
            showerror('Connection error', 'Please specify a device for the arm.')
        elif not self.camera:
            showerror('Connection error', 'Please specify a camera.')
        else:
            # Connection to the robot
            self.robot = PatchClampRobot(self.controller, self.arm, self.camera, self.amplifier, self.pump, False)

            # Setting messages
            self.message = self.robot.message

            # Disable connection buttons and lists
            self.controllist['state'] = 'disabled'
            self.armlist['state'] = 'disabled'
            self.amplist['state'] = 'disabled'
            self.camlist['state'] = 'disabled'
            self.pumplist['state'] = 'disabled'
            self.connection.config(state='disable')

            # Activate all the others buttons
            self.imgsave.config(state='normal', command=self.robot.save_img)
            self.load_calibrate.config(state='normal')
            self.calibrate.config(state='normal')
            self.zero.config(state='normal')
            self.disconnection.config(state='normal')
            self.continuous_meter.config(state='normal')
            self.check_pipette_resistance.config(state='normal')
            self.clamp.config(state='normal', command=self.robot.clamp)
            self.clamp_switch.config(state='normal')

            # Checking changes of robot messages and display them
            self.check_message()
        pass

    def disconnect(self):
        """
        Disconnect the robot. For now reconnection doesn't work (controller not really disconnected)
        :return: 
        """
        # stoping threads linked to the robot
        self.robot.stop()
        del self.robot
        self.robot = None

        # Disable all buttons and enable connection buttons
        self.calibrate.config(state='disable')
        self.imgsave.config(state='disable', command=None)
        self.load_calibrate.config(state='disable')
        self.zero.config(state='disable')
        self.controllist['state'] = 'readonly'
        self.armlist['state'] = 'readonly'
        self.amplist['state'] = 'readonly'
        self.camlist['state'] = 'readonly'
        self.pumplist['state'] = 'readonly'
        self.connection.config(state='normal')
        self.disconnection.config(state='disable')
        self.check_pipette_resistance.config(state='disable')
        self.clamp.config(state='disable', command=None)
        self.clamp_switch.config(state='disable')
        pass

    def calibration(self):
        """
        Launch auto calibration
        :return: 
        """
        if self.robot:
            # Connection to the robot has been established
            if askokcancel('Calibrating',
                           'Please put the tip of the pipette in focus and at the center of the image.',
                           icon=INFO):
                # Pipette in focus and centered: calibrating
                self.robot.event['event'] = 'Calibration'
            pass

    def load_cali(self):
        """
        Loads previous calibration
        :return: 
        """
        if self.robot:
            # Connection to the robot has been established
            if askokcancel('Loading calibration',
                           'Please put the tip of the pipette in focus and at the center of the image.',
                           icon=INFO):
                # Pipette in focus and centered: loading calibration
                self.robot.load_calibration()
            pass

    def reset_pos(self):
        """
        Reset position to null position
        :return: 
        """
        if self.robot:
            self.robot.go_to_zero()
        pass

    def get_res(self):
        """
        Retrieve the resistance metered by robot.
        :return: 
        """
        if self.robot:
            # Connection of robot established
            self.res_value['text'] = self.robot.get_resistance(res_type='text')
            if self.continuous.get():
                # Retrieving continuoulsy enabled
                self.after(10, self.get_res)
        pass

    def get_pot(self):
        """
        Retrieve the resistance metered by robot.
        :return: 
        """
        if self.robot:
            # Connection of robot established
            self.potential_value['text'] = self.robot.get_potential(res_type='text')
            if self.continuous.get():
                # Retrieving continuoulsy enabled
                self.after(10, self.get_pot)
        pass

    def init_patch_clamp(self):
        """
        Checks if conditions for patching are met (pipette resistance)
        :return: 
        """
        if self.robot:
            # Connection of robot established
            self.choose_resistance.select()
            if self.robot.init_patch_clamp():
                # Conditions are met, enable continous resistance metering
                self.continuous_meter.select()
        pass

    def enable_clamp(self):
        """
        Enable/disable calmp when right clicking on the camera window
        :return: 
        """
        if self.robot:
            # Connection of robot established
            self.robot.enable_clamp ^= 1
        pass

    def switch_continuous_meter(self):
        """
        Enable/Disable continuous resistance metering
        :return: 
        """
        if self.robot:
            if self.continuous.get():
                # Continuous metering button is checked, activate continuous metering
                self.robot.set_continuous_res_meter(True)

                #if self.chosen_meter == 1:
                self.get_res()
                #elif self.chosen_meter == 2:
                 #   self.get_pot()
            else:
                # Continuous metering button unchecked, deactivate continuous metering
                self.robot.set_continuous_res_meter(False)
        pass

    def following(self):
        """
        Enable/disable pipette following the camera 
        :return: 
        """
        if self.robot:
            # Connection of robot established, enable folowing if follow button is checked
            self.robot.following = self.follow.get()
        pass

    def check_message(self):
        """
        Retrieve messages from robot and display them when they change
        :return: 
        """
        if self.robot:
            # Connection of robot established
            if self.message != self.robot.message:
                # Message memory is different from actual robot message
                self.message = self.robot.message
                if self.message[:5] == 'ERROR':
                    # The new message is an error, display the message in a new window
                    showerror('ERROR', self.message)

                # Activate the message zone, write the message and deactivate message zone (thus make a read only)
                self.text_zone.config(state='normal')
                self.text_zone.insert(INSERT, self.message+'\n')
                self.text_zone.config(state='disabled')

                # Update memory and actual message: if same messages follow each other, both are retrieve
                self.message = ''
                self.robot.message = ''

            # Check again in 10ms
            self.after(10, self.check_message)
        pass

    def exit(self):
        """
        Close GUI and all threads
        :return: 
        """
        if self.robot:
            # Connection of robot established, disconnecting
            self.robot.stop()
            del self.robot
        # quit GUI
        self.quit()


if __name__ == '__main__':
    root = Tk()
    root.title('Automatic Patch Clamp')
    app = PatchClampGUI(master=root)
    root.resizable(width=False, height=False)
    root.protocol("WM_DELETE_WINDOW", app.exit)
    app.mainloop()
    try:
        root.destroy()
    except TclError:
        # Already destroyed
        pass
