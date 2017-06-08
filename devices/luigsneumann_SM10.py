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
from numpy import zeros

__all__ = ['LuigsNeumann_SM10']

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

        high, low = self.CRC_16(data,len(data))

        # Create hex-string to be sent
        # <syn><ID><byte number>
        send = '16' + ID + '%0.2X' % len(data)

        # <data>
        # Loop over length of data to be sent
        for i in range(len(data)):
            send += '%0.2X' % data[i]

        # <CRC>
        send += '%0.2X%0.2X' % (high,low)

        # Convert hex string to bytes
        sendbytes = binascii.unhexlify(send)

        # Expected response: <ACK><ID><byte number><data><CRC>
        # We just check the first two bytes
        expected = binascii.unhexlify('06'+ID)

        self.port.write(sendbytes)

        answer = self.port.read(nbytes_answer+6)

        if answer[:len(expected)] != expected :
            pass
            #raise serial.SerialException # TODO: something a bit more explicit!
        # We should also check the CRC + the number of bytes
        # Do several reads; 3 bytes, n bytes, CRC

        return answer[4:4+nbytes_answer]

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
        x_hex = binascii.hexlify(struct.pack('>f', x))
        data = [axis, int(x_hex[6:], 16), int(x_hex[4:6], 16), int(x_hex[2:4], 16), int(x_hex[:2], 16)]
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
        x_hex = binascii.hexlify(struct.pack('>f', x))
        data = [axis, int(x_hex[6:], 16), int(x_hex[4:6], 16), int(x_hex[2:4], 16), int(x_hex[:2], 16)]
        self.send_command('004A', data, 0)

    def position_group_test(self, axes):
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

        data = [0xA0] + axes4
        res = self.send_command('A101', data, 0x14)[4:]
        x = zeros(4)
        for i in range(4):
            x[i] = struct.unpack('f', res[i*4:(i+1)*4])[0]
        return x[:len(axes)]

    def absolute_move_group(self, x, axes):
        '''
        Moves the device group of axes to position x.

        Parameters
        ----------
        axes : list of axis numbers
        x : target position in um (vector or list).
        '''
        # First fill in zeros to make 4 axes
        x4 = [0., 0., 0., 0.]
        axes4 = [0, 0, 0, 0]
        x4[:len(x)] = x
        axes4[:len(x)] = axes

        data = [0xA0]+axes4
        for i in range(4):
            x_hex = binascii.hexlify(struct.pack('>f', x4[i]))
            data+= [int(x_hex[6:], 16), int(x_hex[4:6], 16), int(x_hex[2:4], 16), int(x_hex[:2], 16)]
        self.send_command('A048', data, 0)

    def relative_move_group_test(self, x, axes):
        '''
        Moves the device group of axes by relative amount x in um.

        Parameters
        ----------
        axes : list of axis numbers
        x : position shift in um (vector or list).
        '''
        # First fill in zeros to make 4 axes
        x4 = [0., 0., 0., 0.]
        axes4 = [0, 0, 0, 0]
        x4[:len(x)] = x
        axes4[:len(x)] = axes

        data = [0xA0]+axes4
        for i in range(4):
            x_hex = binascii.hexlify(struct.pack('>f', x))
            data+= [int(x_hex[6:], 16), int(x_hex[4:6], 16), int(x_hex[2:4], 16), int(x_hex[:2], 16)]
        self.send_command('A04A', data, 0)

    def stop(self, axis):
        """
        Stop current movements.
        """
        self.send_command('00FF', [axis], 0)

    def set_to_zero(self, axis):
        """
        Set the current position of the axis as the zero position
        :param axis: 
        :return: 
        """
        self.send_command('00F0', [axis], 0)

    def wait_motor_stop(self, axis):
        """
        Wait for the motor to stop
        :param axis: 
        :return: 
        """
        res = 1
        while res:
            res = self.send_command('0120', [axis], 9)
            res = int(binascii.hexlify(struct.unpack('s', res[6])[0])[1])
