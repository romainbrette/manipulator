"""
Generic Device class for manipulators.

To make a new device, one must implement at least:
* position
* absolute_move
"""
from numpy import array
import time

__all__ = ['Device']

class Device(object):
    def __init__(self):
        pass

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

    def position_group(self, axes):
        '''
        Current position along a group of axes.

        Parameters
        ----------
        axes : list of axis numbers

        Returns
        -------
        The current position of the device axis in um (vector).
        '''
        return array([self.position(axis) for axis in axes])

    def absolute_move_group(self, x, axes):
        '''
        Moves the device group of axes to position x.

        Parameters
        ----------
        axes : list of axis numbers
        x : target position in um (vector or list).
        '''
        for xi,axis in zip(x,axes):
            self.absolute_move(xi, axis)

    def relative_move_group(self, x, axes):
        '''
        Moves the device group of axes by relative amount x in um.

        Parameters
        ----------
        axes : list of axis numbers
        x : position shift in um (vector or list).
        '''
        self.absolute_move_group(array(self.position_group(axes))+array(x), axes)

    def stop(self, axis):
        """
        Stops current movements.
        """
        pass

    def wait_until_still(self, axis):
        """
        Waits until motors have stopped.

        Parameters
        ----------
        axes : list of axis numbers
        """
        previous_position = self.position(axis)
        new_position = None
        while (previous_position != new_position):
            previous_position = new_position
            new_position = self.position(axis)
            time.sleep(0.1) # 100 us