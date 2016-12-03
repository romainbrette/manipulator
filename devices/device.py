"""
Generic Device class for manipulators

Notes:
    It could be better to store the position, and have an update() function.
"""

__all__ = ['Device']

class Device(object):
    def __init__(self):
        pass

    def position(self):
        '''
        Returns
        -------
        The current XYZ position of the device in um.
        '''
        pass

    def move(self,v, speed = None):
        '''
        Moves the device to position v, with optional speed.

        Parameters
        ----------
        v : x,y,z vector (array) in um.
        speed : optional speed in um/s.
        '''
