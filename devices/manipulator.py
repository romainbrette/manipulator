"""
Manipulator class contains access to a manipulator and transformed coordinates.
"""
from virtualdevice import VirtualDevice
from device import Device
from numpy import array, ones, zeros, eye, dot

__all__ = ['Manipulator']

class Manipulator(object): # could be a device
    def __init__(self, dev):
        '''
        Parameters
        ----------
        dev : underlying virtual device
        '''
        self.dev = dev
        self.M = eye(3) # Matrix transform
        self.Minv = eye(3) # Inverse of M
        self.x0 = zeros(3) # Offset
        self.x = zeros(3) # Transformed position
        self.y = zeros(3) # Underlying position

    def update(self):
        '''
        Update the position of the manipulator
        '''
        for i in range(3):
            self.y[i] = self.dev.position(i)
        self.x = dot(self.M,self.y)+self.x0

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
        return self.x[axis]

    def move(self, x, axis = None, speed=None):
        '''
        Moves the device axis to position x, with optional speed.

        Parameters
        ----------
        axis: axis number starting at 0
        x : target position in um.
        speed : optional speed in um/s.
        '''
        ytarget = dot(self.Minv, x - self.x0)
        for i in range(3):
            self.dev.move(ytarget[i], i, speed)
