"""
A fake device useful for development.
It has 9 axes, numbered 1 to 9.
"""
from device import Device
from numpy import zeros, array

__all__ = ['FakeDevice']

class FakeDevice(Device):
    def __init__(self):
        Device.__init__(self)
        self.x = zeros(9) # Position of all axes

    def position(self, axis):
        '''
        Current position along an axis.

        Parameters
        ----------
        axis : axis number

        Returns
        -------
        The current position of the device axis in um.
        '''
        return self.x[axis-1]

    def absolute_move(self, x, axis):
        '''
        Moves the device axis to position x.

        Parameters
        ----------
        axis: axis number
        x : target position in um.
        '''
        self.x[axis-1] = x
