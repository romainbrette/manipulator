"""
A class for access to a particular XYZ unit managed by a device

TODO: group queries, based on array or list
"""
from device import *
from numpy import array
from time import sleep

__all__ = ['XYZUnit']


class XYZUnit(Device):
    def __init__(self, dev, axes):
        '''
        Parameters
        ----------
        dev : underlying device
        axes : list of 3 axis indexes
        '''
        Device.__init__(self)
        self.dev = dev
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
            #return array([self.dev.position(self.axes[axis]) for axis in range(len(self.axes))])
            return self.dev.position_group(self.axes)
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
            #for i, axis in enumerate(self.axes):
            #    self.dev.absolute_move(x[i], axis)
            self.dev.absolute_move_group(x, self.axes)
        else:
            self.dev.absolute_move(x, self.axes[axis])
        sleep(.02)

    def relative_move(self, x, axis = None):
        '''
        Moves the device axis by relative amount x in um.

        Parameters
        ----------
        axis : axis number starting at 0; if None, all XYZ axes
        x : position shift in um.
        '''
        if axis is None:
            # then we move all axes
            #for i, axis in enumerate(self.axes):
            #    self.dev.relative_move(x[i], axis)
            self.dev.relative_move_group(x, self.axes)
        else:
            self.dev.relative_move(x, self.axes[axis])
        sleep(.02)

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
            self.dev.set_to_zero([self.axes[axis]])
        sleep(.02)

    def go_to_zero(self, axis):
        """
        Make axis go to zero position
        :return: 
        """
        if isinstance(axis, list):
            for i in axis:
                self.go_to_zero(i)
        else:
            self.dev.go_to_zero([self.axes[axis]])
        sleep(.02)

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
            self.dev.wait_motor_stop([self.axes[axis]])
        sleep(.02)
