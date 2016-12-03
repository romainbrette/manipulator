"""
Device class for the Luigs and Neumann SM-10 manipulator controller.

Adapted from Michael Graupner's LandNSM5 class.
"""
from serialdevice import SerialDevice
import serial
import binascii
import time

__all__ = ['LuigsNeumann_SM10']

class LuigsNeumann_SM10(SerialDevice):
    def __init__(self, port_name = 'COM5'):
        # Note that the port name is arbitrary, it should be set or found out
        SerialDevice.__init__(self)

        # Open the serial port; 1 second time out
        self.port = serial.Serial(port=port_name, baudrate=115200, bytesize=serial.EIGHTBITS,
                                  parity=serial.PARITY_NONE,
                                  stopbits=serial.STOPBITS_ONE, timeout=1.)

        # except serial.SerialException # in case one wants to catch it

    def send_command(self, ID, data, expected, nbytes_answer):
        '''
        Send a command to the controller
        '''

        high, low = self.CRC_16(data,len(data))

        # Create hex-string to be sent
        send = '16' + ID + '%0.2X' % len(data)

        # Loop over length of data to be sent
        for i in range(len(data)):
            send += '%0.2X' % data[i]
        send += '%0.2X%0.2X' % (high,low)

        # Convert hex string to bytes
        sendbytes = binascii.unhexlify(send)

        nLoops = 0
        while True:
            # Write, wait, and read
            self.port.write(sendbytes)
            time.sleep(0.05) # 50 us; could be changed
            answer = self.port.read(nbytes_answer)

            # Compare answer with answer mask, if true: break, if false : redo
            if answer[:len(expected)] == expected :
				break
			if nLoops >= self.maxLoops:
				print 'Command was not successful!'
				break
			nLoops += 1
		return answer
