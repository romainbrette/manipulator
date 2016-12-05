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

    def position(self, axis = None):
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

    def move(self, x, axis = None, speed = None):
        '''
        Moves the device axis to position x, with optional speed.

        Parameters
        ----------
        axis: axis number
        x : target position in um.
        speed : optional speed in um/s.
        '''
        pass
