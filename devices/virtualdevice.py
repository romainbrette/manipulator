"""
A class for access to a particular manipulator managed by a device
"""
from device import *
from numpy import array

__all__ = ['VirtualDevice']


class VirtualDevice(Device):
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

    def position(self, axis = None):
        '''
        Current position along an axis.

        Parameters
        ----------
        axis : axis number starting at 0

        Returns
        -------
        The current position of the device axis in um.
        '''
        if axis is None: # all positions in a vector
            return array([self.dev.position(self.axes[axis]) for axis in range(self.naxes)])
        else:
            return self.dev.position(self.axes[axis])

    def move(self, x, axis = None, speed=None):
        '''
        Moves the device axis to position x, with optional speed.

        Parameters
        ----------
        axis: axis number starting at 0
        x : target position in um.
        speed : optional speed in um/s.
        '''
        if axis is None:
            axes = self.axes # then we move all axes
        else:
            axes = [self.axes[axis]]

        for axis in axes:
            self.dev.move(x, axis, speed)
