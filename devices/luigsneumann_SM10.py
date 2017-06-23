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
        self.port.write(sendbytes)

        if nbytes_answer >= 0:
            # Expected response: <ACK><ID><byte number><data><CRC>
            # We just check the first two bytes
            expected = binascii.unhexlify('06' + ID)

            answer = self.port.read(nbytes_answer + 6)
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

    def slow_speed(self, axis):
        '''
        Query the slow speed setting for a given axis
        '''
        res = self.send_command('0190', [axis], 1)
        return struct.unpack('b', res)[0]

    def fast_speed(self, axis):
        '''
        Query the fast speed setting for a given axis
        '''
        res = self.send_command('0143', [axis], 1)
        return struct.unpack('b', res)[0]

    def set_slow_speed(self, axis, speed):
        '''
        Query the slow speed setting for a given axis
        '''
        self.send_command('018F', [axis, speed], 0)

    def set_fast_speed(self, axis, speed):
        '''
        Query the slow speed setting for a given axis
        '''
        self.send_command('0144', [axis, speed], 0)

    def absolute_move(self, x, axis, fast=True):
        '''
        Moves the device axis to position x.

        Parameters
        ----------
        axis: axis number (starting at 1)
        x : target position in um.
        speed : optional speed in um/s.
        '''
        self.absolute_move_group([x], [axis], fast=fast)

    def relative_move(self, x, axis, fast=True):
        '''
        Moves the device axis by relative amount x in um.

        Parameters
        ----------
        axis: axis number
        x : position shift in um.
        '''
        self.relative_move_group([x], [axis], fast=fast)

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
        ret = struct.unpack('4b4f', self.send_command('A101', [0xA0] + axes4, 20))
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
        self.send_command(ID, [0xA0] + axes4 + pos, -1)

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
        self.send_command(ID, [0xA0] + axes4 + pos, -1)

    def single_step(self, axis, steps):
        '''
        '''
        ID = '01E8'
        if steps < 0:
            steps += 256
        self.send_command(ID, [axis, steps], 0)

    def set_single_step_factor(self, axis, factor):
        ID = '019F'
        if factor < 0:
            factor += 256
        data = (axis, factor)
        self.send_command(ID, data, 0)

    def stop(self, axis):
        """
        Stop current movements on one axis.
        """
        # Note that the "collection command" STOP (A0FF) only stops
        # a move started with "Procedure + ucVelocity"
        ID = '00FF'
        self.send_command(ID, [axis], 0)

    def set_to_zero(self, axes):
        """
        Set the current position of the axes as the zero position
        :param axes:
        :return: 
        """
        # # collection command does not seem to work...
        # ID = 'A0F0'
        # address = group_address(axes)
        # self.send_command(ID, address, -1)
        ID = '00F0'
        for axis in axes:
            self.send_command(ID, [axis], 0)

    def go_to_zero(self, axis):
        """
        Make axis go to zero position
        :return: 
        """
        ID = '0024'
        for axes in axis:
            self.send_command(ID, [axes], 0)

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
        time.sleep(0.1)  # right after a motor command the motors are not moving yet
        ret = struct.unpack('20B', self.send_command('A120', data, 20))
        moving = [ret[6 + i*4] for i in range(len(axes))]
        is_moving = any(moving)
        while is_moving:
            time.sleep(0.05)
            ret = struct.unpack('20B', self.send_command('A120', data, 20))
            moving = [ret[6 + i * 4] for i in range(len(axes))]
            is_moving = any(moving)


if __name__ == '__main__':
    # Calculate the example group addresses from the documentation
    print(''.join(['%x' % a for a in group_address([1])]))
    print(''.join(['%x' % a for a in group_address([3, 6, 9, 12, 15, 18])]))
    print(''.join(['%x' % a for a in group_address([4, 5, 6, 7, 8, 9, 10, 11, 12])]))
    sm10 = LuigsNeumann_SM10('COM3')

    sm10.absolute_move(1000, 7)
    sm10.wait_motor_stop([7])
    sm10.set_single_step_factor(7, 2)
    sm10.set_single_step_factor(8, 2)
    # sm10.single_step(7, 1)
    # print sm10.position(7)
    # sm10.single_step(7, 1)
    # print sm10.position(7)
    # time.sleep(1)
    print sm10.position(8)
    sm10.single_step(8, 1)
    time.sleep(1)
    print sm10.position(8)
    sm10.single_step(8, -2)
    time.sleep(1)
    print sm10.position(8)