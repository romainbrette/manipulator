"""
The SerialDevice class:
a device that communicates through the serial port.
"""
from device import Device
import serial
import ctypes

__all__ = ['SerialDevice']

class SerialDevice(Device):
    '''
    A device that communicates through the serial port.
    '''
    def __init__(self):
        Device.__init__(self)

        # Open the serial port
        #self.port = serial.Serial(port='COM5', baudrate=38400, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
        #                     stopbits=serial.STOPBITS_ONE, timeout=self.timeOut)
        #except serial.SerialException

    def __del__(self):
        self.port.close()

    def CRC_16(self, butter, length):
        # Calculate CRC-16 checksum based on the data sent
        #
        crc_polynom = 0x1021
        crc = 0
        n = 0
        lll = length
        while (lll > 0):
            crc = crc ^ butter[n] << 8
            for _ in range(8):
                if (crc & 0x8000):
                    crc = crc << 1 ^ crc_polynom
                else:
                    crc = crc << 1
            lll -= 1
            n += 1
        crc_high = ctypes.c_ubyte(crc >> 8)
        crc_low = ctypes.c_ubyte(crc)
        return (crc_high.value, crc_low.value)

