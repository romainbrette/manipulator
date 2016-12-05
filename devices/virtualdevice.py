"""
A class for access to a particular manipulator managed by a device
"""
from device import *

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

    def position(self, axis):
        '''
        Current position along an axis.

        Parameters
        ----------
        axis : axis number starting at 0

        Returns
        -------
        The current position of the device axis in um.
        '''
        return self.dev.position(self.axes[axis])

    def move(self, axis, x, speed=None):
        '''
        Moves the device axis to position x, with optional speed.

        Parameters
        ----------
        axis: axis number starting at 0
        x : target position in um.
        speed : optional speed in um/s.
        '''
        self.dev.move(self.axes[axis], x, speed)
