"""
A class for access to a particular XYZ unit managed by a device

TODO: group queries, based on array or list
"""
from device import *
from numpy import array

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
        axis : axis number starting at 0

        Returns
        -------
        The current position of the device axis in um.
        '''
        if axis is None: # all positions in a vector
            return array([self.dev.position(self.axes[axis]) for axis in range(self.naxes)])
        else:
            return self.dev.position(self.axes[axis])

    def absolute_move(self, x, axis = None):
        '''
        Moves the device axis to position x in um.

        Parameters
        ----------
        axis: axis number starting at 0
        x : target position in um.
        '''
        if axis is None:
            # then we move all axes
            for i, axis in enumerate(self.axes):
                self.dev.absolute_move(x[i], axis)
        else:
            self.dev.absolute_move(x, self.axes[axis])

    def relative_move(self, x, axis = None):
        '''
        Moves the device axis by relative amount x in um.

        Parameters
        ----------
        axis: axis number
        x : position shift in um.
        '''
        if axis is None:
            # then we move all axes
            for i, axis in enumerate(self.axes):
                self.dev.relative_move(x[i], axis)
        else:
            self.dev.relative_move(x, self.axes[axis])

    def save(self, name):
        self.memory[name] = self.position()

    def load(self, name):
        self.absolute_move(self.memory[name])
