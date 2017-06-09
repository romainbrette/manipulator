"""
Device class for the Luigs and Neumann SM-10 manipulator controller.

Adapted from Michael Graupner's LandNSM5 class.

TODO: group commands
"""
from serialdevice import SerialDevice
import serial
import binascii
import time
import struct
import numpy as np

__all__ = ['LuigsNeumann_SM10']


def group_address(axes):
    all_axes = np.sum(2 ** (np.array(axes) - 1))
    # The group address is fixed at 9 bytes
    address = binascii.unhexlify('%.18x' % all_axes)
    return struct.unpack('9B', address)


class LuigsNeumann_SM10(SerialDevice):
    def __init__(self, name = None):
        # Note that the port name is arbitrary, it should be set or found out
        SerialDevice.__init__(self, name)

        # Open the serial port; 1 second time out
        self.port.baudrate = 115200
        self.port.bytesize = serial.EIGHTBITS
        self.port.parity=serial.PARITY_NONE
        self.port.stopbits=serial.STOPBITS_ONE
        self.port.timeout=1. #None # blocking

        self.port.open()

    def send_command(self, ID, data, nbytes_answer):
        '''
        Send a command to the controller
        '''
        high, low = self.CRC_16(data, len(data))

        # Create hex-string to be sent
        # <syn><ID><byte number>
        send = '16' + ID + '%0.2X' % len(data)

        # <data>
        # Loop over length of data to be sent
        for i in range(len(data)):
            send += '%0.2X' % data[i]

        # <CRC>
        send += '%0.2X%0.2X' % (high, low)
        # Convert hex string to bytes
        sendbytes = binascii.unhexlify(send)
        self.write(sendbytes)

        if nbytes_answer >= 0:
            # Expected response: <ACK><ID><byte number><data><CRC>
            # We just check the first two bytes
            expected = binascii.unhexlify('06' + ID)

            answer = self.read(nbytes_answer + 6)
            if answer[:len(expected)] != expected:
                msg = "Expected answer '%s', got '%s' " \
                      "instead" % (binascii.hexlify(expected),
                                   binascii.hexlify(answer[:len(expected)]))
                raise serial.SerialException(msg)
            # We should also check the CRC + the number of bytes
            # Do several reads; 3 bytes, n bytes, CRC
            return answer[4:4 + nbytes_answer]
        else:
            return None

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
        res = self.send_command('0101', [axis], 4)
        return struct.unpack('f', res)[0]

    def absolute_move(self, x, axis):
        '''
        Moves the device axis to position x.
        It uses the fast movement command.

        Parameters
        ----------
        axis: axis number (starting at 1)
        x : target position in um.
        speed : optional speed in um/s.
        '''
        data = [axis] + [b for p in x for b in bytearray(struct.pack('f', p))]
        self.send_command('0048', data, 0)

    def relative_move(self, x, axis):
        '''
        Moves the device axis by relative amount x in um.
        It uses the fast command.

        Parameters
        ----------
        axis: axis number
        x : position shift in um.
        '''
        data = [axis] + [b for p in x for b in bytearray(struct.pack('f', p))]
        self.send_command('004A', data, 0)

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
        # First fill in zeros to make 4 axes
        axes4 = [0, 0, 0, 0]
        axes4[:len(axes)] = axes
        ret = struct.unpack('4b4f', self.send('A101', [0xA0] + axes4, 20))
        assert all(r == a for r, a in zip(ret[:3], axes))
        return ret[4:7]

    def absolute_move_group(self, x, axes, fast=True):
        '''
        Moves the device group of axes to position x.

        Parameters
        ----------
        axes : list of axis numbers
        x : target position in um (vector or list)
        '''
        ID = 'A048' if fast else 'A049'

        axes4 = [0, 0, 0, 0]
        axes4[:len(axes)] = axes
        pos4 = [0, 0, 0, 0]
        pos4[:len(x)] = x

        pos = [b for p in pos4 for b in bytearray(struct.pack('f', p))]

        # Send move command
        self.send(ID, [0xA0] + axes + [0] + pos, -1)

    def relative_move_group(self, x, axes, fast=True):
        '''
        Moves the device group of axes by relative amount x in um.

        Parameters
        ----------
        axes : list of axis numbers
        x : position shift in um (vector or list).
        '''
        ID = 'A04A' if fast else 'A04B'

        axes4 = [0, 0, 0, 0]
        axes4[:len(axes)] = axes
        pos4 = [0, 0, 0, 0]
        pos4[:len(x)] = x

        pos = [b for p in pos4 for b in bytearray(struct.pack('f', p))]

        # Send move command
        self.send(ID, [0xA0] + axes + [0] + pos, -1)

    def stop(self, axes):
        """
        Stop current movements.
        """
        ID = 'A0FF'
        address = group_address(axes)
        self.send(ID, address, -1)

    def set_to_zero(self, axes):
        """
        Set the current position of the axes as the zero position
        :param axes:
        :return: 
        """
        ID = 'A0F0'
        address = group_address(axes)
        self.send(ID, address, -1)

    def wait_motor_stop(self, axes):
        """
        Wait for the motor to stop
        On SM10, motors' commands seems to block
        :param axes:
        :return: 
        """
        axes4 = [0, 0, 0, 0]
        axes4[:len(axes)] = axes
        data = [0xA0] + axes + [0]
        ret = struct.unpack('20B', self.send('A120', data, 20))
        moving = [ret[6 + i*4] for i in range(len(axes))]
        is_moving = any(moving)
        while is_moving:
            ret = struct.unpack('20B', self.send('A120', data, 20))
            moving = [ret[6 + i * 4] for i in range(len(axes))]
            is_moving = any(moving)

if __name__ == '__main__':
    # Calculate the example group addresses from the documentation
    print(''.join(['%x' % a for a in group_address([1])]))
    print(''.join(['%x' % a for a in group_address([3, 6, 9, 12, 15, 18])]))
    print(''.join(['%x' % a for a in group_address([4, 5, 6, 7, 8, 9, 10, 11, 12])]))
