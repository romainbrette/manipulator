"""
Device class for the Luigs and Neumann SM-10 manipulator controller.

Adapted from Michael Graupner's LandNSM5 class.
"""
from serialdevice import SerialDevice
import serial
import binascii
import time
import struct

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
        self.port.timeout=None # blocking

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
            raise serial.SerialException # TODO: something a bit more explicit!
        # We should also check the CRC + the number of bytes
        # Do several reads; 3 bytes, n bytes, CRC

        return answer[4:4+nbytes_answer]

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
        res = self.send_command('0101', [axis], 4)
        return struct.unpack('f', res)[0]

    def move(self, x, axis = None, speed = None):
        '''
        Moves the device axis to position x, with optional speed.
        It uses the fast movement command (speed not used).

        Parameters
        ----------
        axis: axis number (starting at 1)
        x : target position in um.
        speed : optional speed in um/s.
        '''
        x_hex = binascii.hexlify(struct.pack('>f', x))
        data = [axis, int(x_hex[6:], 16), int(x_hex[4:6], 16), int(x_hex[2:4], 16), int(x_hex[:2], 16)]
        self.send_command('0048', data, 0)
