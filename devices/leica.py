"""
A Z Unit for a Leica microscope, using MicroManager.
Communication through serial COM port.
"""
from device import *
import sys
sys.path.append('C:\\Program Files\\Micro-Manager-1.4')
import MMCorePy

__all__ = ['Leica']


class Leica(Device):
    def __init__(self, name = 'COM1'):
        '''
        Parameters
        ----------
        name : port name
        '''
        Device.__init__(self)
        self.memory = dict() # A dictionary of positions

        self.port_name = name
        mmc = MMCorePy.CMMCore()
        self.mmc = mmc
        mmc.loadDevice(name, 'SerialManager', name)
        mmc.setProperty(name, 'AnswerTimeout', 500.0)
        mmc.setProperty(name, 'BaudRate', 19200)
        mmc.setProperty(name, 'DelayBetweenCharsMs', 0.0)
        mmc.setProperty(name, 'Handshaking', 'Off')
        mmc.setProperty(name, 'Parity', 'None')
        mmc.setProperty(name, 'StopBits', 1)
        mmc.setProperty(name, 'Verbose', 1)
        mmc.loadDevice('Scope', 'LeicaDMI', 'Scope')
        mmc.loadDevice('FocusDrive', 'LeicaDMI', 'FocusDrive')
        mmc.setProperty('Scope', 'Port', name)
        mmc.initializeDevice(name)
        mmc.initializeDevice('Scope')
        mmc.initializeDevice('FocusDrive')
        mmc.setFocusDevice('FocusDrive')

    def __del__(self):
        self.mmc.unloadDevice('FocusDrive')
        self.mmc.unloadDevice('Scope')
        self.mmc.unloadDevice(self.port_name)

    def position(self, axis = None):
        '''
        Current position along an axis.

        Parameters
        ----------
        axis : this is ignored

        Returns
        -------
        The current position of the device axis in um.
        '''
        return self.mmc.getPosition()

    def absolute_move(self, x, axis = None):
        '''
        Moves the device axis to position x in um.

        Parameters
        ----------
        axis : this is ignored
        x : target position in um.
        '''
        self.mmc.setPosition(x)

    def relative_move(self, x, axis = None):
        '''
        Moves the device axis by relative amount x in um.

        Parameters
        ----------
        axis : this is ignored
        x : position shift in um.
        '''
        self.mmc.setRelativePosition(x)

    def save(self, name):
        self.memory[name] = self.position()

    def load(self, name):
        self.absolute_move(self.memory[name])


if __name__ == '__main__':
    import time

    leica = Leica()

    time.sleep(1)  # the microscope gives a wrong position in the very beginning, so wait a bit

    print leica.position()
    leica.relative_move(-50)
    time.sleep(1)
    print leica.position()
