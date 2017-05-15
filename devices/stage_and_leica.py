"""
An XYZUnit made of an XY stage and a Leica microscope
"""
from device import *

__all__ = ['XYZUnit']


class StageAndLeica(Device):
    def __init__(self, dev, axes):
        '''
        Parameters
        ----------
        dev : underlying device for the stage
        axes : list of 2 axis indexes
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


if __name__ == '__main__':
    import time,sys

    sys.path.append('C:\\Program Files\\Micro-Manager-1.4')
    import MMCorePy

    print "Setting up camera and microscope...",
    mmc = MMCorePy.CMMCore()
    mmc.loadDevice('COM1', 'SerialManager', 'COM1')
    mmc.setProperty('COM1', 'AnswerTimeout', 500.0)
    mmc.setProperty('COM1', 'BaudRate', 19200)
    mmc.setProperty('COM1', 'DelayBetweenCharsMs', 0.0)
    mmc.setProperty('COM1', 'Handshaking', 'Off')
    mmc.setProperty('COM1', 'Parity', 'None')
    mmc.setProperty('COM1', 'StopBits', 1)
    mmc.setProperty('COM1', 'Verbose', 1)
    mmc.loadDevice('Scope', 'LeicaDMI', 'Scope')
    mmc.loadDevice('FocusDrive', 'LeicaDMI', 'FocusDrive')
    mmc.setProperty('Scope', 'Port', 'COM1')
    mmc.initializeDevice('COM1')
    mmc.initializeDevice('Scope')
    mmc.initializeDevice('FocusDrive')
    mmc.setFocusDevice('FocusDrive')
    time.sleep(1)  # the microscope gives a wrong position in the very beginning, so wait a bit

    print mmc.getPosition()
    mmc.setRelativePosition(-50)
    time.sleep(1)
    print mmc.getPosition()
    mmc.unloadDevice('FocusDrive')
    mmc.unloadDevice('Scope')
    mmc.unloadDevice('COM1')
