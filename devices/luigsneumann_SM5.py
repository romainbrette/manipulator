"""
Device class for the Luigs and Neumann SM-5 manipulator controller.

Adapted from Michael Graupner's LandNSM5 class.

"""
from serialdevice import SerialDevice
import serial
import binascii
import time
import struct
import warnings
from numpy import zeros

__all__ = ['LuigsNeumann_SM5']

verbose = True

class LuigsNeumann_SM5(SerialDevice):
    def __init__(self, name=None):
        # Note that the port name is arbitrary, it should be set or found out
        SerialDevice.__init__(self, name)

        # Open the serial port; 1 second time out
        self.port.baudrate = 38400
        self.port.bytesize = serial.EIGHTBITS
        self.port.parity=serial.PARITY_NONE
        self.port.stopbits=serial.STOPBITS_ONE
        self.port.timeout=0.1 #None is blocking; 0 is non blocking

        self.port.open()
        self.established_time = time.time()
        self.establish_connection()

    def send_command(self, ID, data, nbytes_answer, ack_ID=''):
        '''
        Send a command to the controller
        '''
        now = time.time()
        if now - self.established_time > 3:
            self.establish_connection()
        self.established_time = now

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

        expected = binascii.unhexlify('06' + ack_ID)

        self.port.write(sendbytes)

        answer = self.port.read(nbytes_answer+6)

        if answer[:len(expected)] != expected :
            warnings.warn('Did not get expected response for command with ID ' + ID +' ; resending')
            # Resend
            return self.send_command(ID, data, nbytes_answer, ack_ID)

        return answer[4:4+nbytes_answer]

    def establish_connection(self):
        if verbose:
            print "establishing connection"
        self.established_time = time.time()
        self.send_command('0400', [], 0, ack_ID='040b')
        if verbose:
            print "connection established"

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

    def position_second_counter(self, axis):
        '''
        Current position along an axis.

        Parameters
        ----------
        axis : axis number (starting at 1)

        Returns
        -------
        The current position of the device axis in um.
        '''
        res = self.send_command('0131', [axis], 4)
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
        # TODO: always goes fast (use 0049 for slow)
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
        for axes in axis:
            self.send_command('00f0', [axes], 0)

    def set_to_zero_second_counter(self, axes):
        """
        Set the current position of the axes as the zero position
        :param axes:
        :return:
        """
        # # collection command does not seem to work...
        # ID = 'A0F0'
        # address = group_address(axes)
        # self.send_command(ID, address, -1)
        ID = '0132'
        for axis in axes:
            self.send_command(ID, [axis, 02], 0)

    def go_to_zero(self, axis):
        """
        Make axis go to zero position
        :return: 
        """
        ID = '0024'
        for axes in axis:
            self.send_command(ID, [axes], 0)

    def single_step(self, axis, steps):
        '''
        Moves the given axis using the StepIncrement or StepDecrement command.
        Using a steps argument different from 1 (or -1) simply sends multiple
        StepIncrement/StepDecrement commands.
        Uses distance and velocity set by `set_single_step_distance` resp.
        `set_single_step_velocity`.
        '''
        if steps > 0:
            ID = '0140'
        else:
            ID = '0141'
        for _ in range(int(abs(steps))):
            self.send_command(ID, [axis], 0)
            time.sleep(0.02)

    def set_single_step_distance(self, axis, distance):
        '''
        Distance (in um) for `single_step`.
        '''
        if distance > 255:
            print('Step distance too long, setting distance at 255um')
            distance = 255
        ID = '013a'
        data = [axis] + list(bytearray(struct.pack('f', distance)))
        self.send_command(ID, data, 0)

    def wait_motor_stop(self, axis):
        """
        Wait for the motor to stop
        :param axis: 
        :return: 
        """
        res = 1
        while res:
            res = self.send_command('0120', axis, 7)
            res = int(binascii.hexlify(struct.unpack('s', res[6])[0])[1])


if __name__ == '__main__':
    sm5 = LuigsNeumann_SM5('COM3')

    """
    print 'getting positions:'

    for ax in range(1, 9):
       print ax, sm5.position(axis=ax)

    time.sleep(2)

    print 'moving first manipulator (3 axes)'
    sm5.relative_move_group([50, 50, 50], [1, 2, 3])

    time.sleep(2)

    print 'moving second manipulator (3 axes)'
    sm5.relative_move_group([50, 50, 50], [4, 5, 6])

    time.sleep(2)

    print 'moving stage (2 axes)'
    sm5.relative_move_group([50, 50], [7, 8])
    """

    """
    Apparently: with two successive absolute moves, the second
    cancels the first. With two successive relative moves, a sort of random
    result is obtained, probably because the second cancels the first at midcourse.
    """

    for i in range(5):
        print sm5.position(1)
        sm5.absolute_move(1000,1)
        time.sleep(1)
        print sm5.position(1)
        sm5.absolute_move(1128,1)
        print sm5.position(1)
        time.sleep(1)
