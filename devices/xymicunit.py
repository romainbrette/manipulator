"""
An XYZ unit made of an XY stage and another device representing the microscope Z axis
"""
from device import *
from numpy import array

__all__ = ['XYMicUnit']


class XYMicUnit(Device):
    def __init__(self, dev, dev_mic, axes):
        '''
        Parameters
        ----------
        dev : underlying device for the XY stage
        dev_mic : underlying device for the Z axis
        axes : list of 2 axis indexes
        '''
        Device.__init__(self)
        self.dev = dev
        self.dev_mic = dev_mic
        self.axes = axes
        self.memory = dict() # A dictionary of positions

    def position(self, axis = None):
        '''
        Current position along an axis.

        Parameters
        ----------
        axis : axis number starting at 0; if None, all XYZ axes

        Returns
        -------
        The current position of the device axis in um.
        '''
        if axis is None: # all positions in a vector
            return array(list(self.dev.position_group(self.axes)) + [self.dev_mic.position()])
        else:
            if axis == 2: # Z
                return self.dev_mic.position()
            else:
                return self.dev.position(self.axes[axis])

    def absolute_move(self, x, axis = None):
        '''
        Moves the device axis to position x in um.

        Parameters
        ----------
        axis : axis number starting at 0; if None, all XYZ axes
        x : target position in um.
        '''
        if axis is None:
            # then we move all axes
            self.dev.absolute_move_group(x, self.axes)
            self.dev_mic.absolute_move(x)
        else:
            if axis == 2: # Z
                self.dev_mic.absolute_move(x)
            else:
                self.dev.absolute_move(x, self.axes[axis])

    def relative_move(self, x, axis = None):
        '''
        Moves the device axis by relative amount x in um.

        Parameters
        ----------
        axis : axis number starting at 0; if None, all XYZ axes
        x : position shift in um.
        '''
        if axis is None:
            self.dev.relative_move_group(x, self.axes)
            self.dev_mic.relative_move(x)
        else:
            if axis == 2: # Z
                self.dev_mic.relative_move(x)
            else:
                self.dev.relative_move(x, self.axes[axis])

    def save(self, name):
        self.memory[name] = self.position()

    def load(self, name):
        self.absolute_move(self.memory[name])

    def stop(self, axis = None):
        """
        Stop current movements.
        """
        if axis is None:
            # then we stop all axes
            for i, axis in enumerate(self.axes):
                self.dev.stop(axis)
            self.dev_mic.stop()
        else:
            if axis == 2:
                self.dev_mic.stop()
            else:
                self.dev.stop(self.axes[axis])

    def set_to_zero(self, axis):
        """
        Set the current position of the axis as the zero position
        :param axis: 
        :return: 
        """
        if isinstance(axis, list):
            for i in axis:
                self.set_to_zero(i)
        else:
            if axis == 2:
                self.dev_mic.set_to_zero()
            else:
                self.dev.set_to_zero([self.axes[axis]])

    def go_to_zero(self, axis):
        """
        Make axis go to zero position
        :return: 
        """
        if isinstance(axis, list):
            for i in axis:
                self.go_to_zero(i)
        else:
            if axis == 2:
                self.dev_mic.go_to_zero()
            else:
                self.dev.go_to_zero([self.axes[axis]])

    def wait_motor_stop(self, axis):
        """
        Wait for the motor to stop
        :param axis: 
        :return: 
        """
        if isinstance(axis, list):
            for i in axis:
                self.wait_motor_stop(i)
        else:
            if axis == 2:
                self.dev_mic.wait_motor_stop()
            else:
                self.dev.wait_motor_stop([self.axes[axis]])

if __name__ == '__main__':
    from luigsneumann_SM5 import *
    from leica import *
    from time import sleep

    sm5 = LuigsNeumann_SM5('COM3')
    mic = Leica('COM1')
    stage = XYMicUnit(sm5, mic, [7,8])

    sleep(1) # waiting for Leica microscope to be ready

    print stage.position()
    print mic.position()
