"""
Generic Device class for manipulators

Notes:
    It could be better to store the position, and have an update() function.
"""
from numpy import array

__all__ = ['Device']

class Device(object):
    def __init__(self):
        pass

    def position(self, axis):
        '''
        Current position along an axis.

        Parameters
        ----------
        axis : axis number (starting at 1)

        Returns
        -------
        The current position of the device axis in um.
        '''
        return 0. # fake

    def absolute_move(self, x, axis):
        '''
        Moves the device axis to position x.

        Parameters
        ----------
        axis: axis number
        x : target position in um.
        '''
        pass

    def relative_move(self, x, axis):
        '''
        Moves the device axis by relative amount x in um.

        Parameters
        ----------
        axis: axis number
        x : position shift in um.
        '''
        self.absolute_move(self.position(axis)+x, axis)
