# LandNSM5 : A python class for communicating with the Luigs & Neumann SM-5 control box.
# 
# LandNSM5 implements a class for communicating with a Luigs & Neumann SM-5
#   control box to control the manipulators. The SM-5 must be connected with 
#   a USB cable.
#   The SM-7 or SM-8-4 control boxes might be accessed similarly, but this 
#   has not been tested. 
#   
#
# This class uses the python "serial" package which allows for communication
#   with serial devices through 'write' and 'read'. 
#   The communication properties (BaudRate, Terminator, etc.) are 
#   set when invoking the serial object with serial.Serial(..). For the SM-5:
#   The Baud rate is 38400 Baud, 8 Data bit, NoParity and 1 Stopbit after 
#   switch power on (see 'Interface description V1.8.pdf' manual). 
#
#
# Methods:
#   Create the object. The object is opened with serial.Serial.
#       obj = LandNSM5()
#
#   Various functions from the manual are implemented such as
#       - goSteps()
#       - stepSlowDistance(...)
#	- goVariableFastToAbsolutePosition(...)
#	- goVariableSlowToAbsolutePosition(...)
# 	- goVariableFastToRelativePosition(...)
#	- stepIncrement(...)
# 	- stepDecrement(...)
# 	- switchOffAxis(...)
#	- switchOnAxis(...)
#	- setAxisToZero(...)
#	- getPosition(...)
#
#	See below for required input arguments. 
#	Futher functions can be easily implemented from the manual following the 
#	structure of the class fuctions. 
#
# Properties:
#   verbose - The level of messages displayed (0 or 1). 
#
#
# Example session:
#
#In [1]: import LandNSM5_1
#
#In [2]: sm5 = LandNSM5_1.LandNSM5()
# Serial<id=0x98b0860, open=True>(port='COM5', baudrate=38400, bytesize=8, parity='N', stopbits=1, timeout=1, xonxoff=False, rtscts=False, dsrdtr=False)
# SM5 ready
#
#In [3]: pos = sm5.getPosition(1,'x')
# Establish connection to SM5 .  established
# send 0101 16010101011021 16 33
# done

# In [4]: print pos
# -3481.796875

# In [5]: sm5.goVariableFastToRelativePosition(1,'x',-15.)
# Establish connection to SM5 .  established
# send 004a 16004a0501000070C16B65 107 101
# done
# 
# In [6]: del sm5
#
#
# Michael Graupner
# michael.graupner@parisdescartes.fr
# v1 2014-09-23
#
#

import serial
import struct
import time 
import sys
from numpy import * 
import binascii
import ctypes

#################################################################
# Class which allows interaction with the Luigs and Neumann manipulator SM5
class LandNSM5 :
	#################################################################
	# constructor
	def __init__(self):
		self.verbose = 0 # level of messages
		self.timeOut = 1 # timeout in sec
		self.establishConnectionHold = 3. # time in seconds a connection remains established
		self.sleepTime = 0.1
		self.maxLoops = 10
		# make sure connection is established at the first call
		self.timeWhenEstablished = time.time() - self.establishConnectionHold
		# initialize serial connection to controller
		try:
			self.ser = serial.Serial(port='COM5',baudrate=38400,bytesize=serial.EIGHTBITS,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,timeout=self.timeOut)
			#self.ser = 
			self.connected = 1
			if self.verbose:
				print self.ser
				print 'SM5 ready'
			#return 0
		except serial.SerialException:
			print 'No connection to Luigs and Neumann SM5 could be established!'
			self.connected = 0
			#sys.exit(1)
		#return self.connected
	#################################################################
	# destructor
	def __del__(self):
		try:
			self.ser.close()
		except AttributeError:
			pass
		if self.verbose : 
			print 'Connection to Luigs and Neumann SM5 closed'
	#################################################################
	# send command to controller
	def sendCommand(self,ID,nBytes,deviceData,response,nBytesRes):
		#
		# establish connection before each command (connection is lost after 3 sec)
		self.timePassed = time.time()
		if (self.timePassed-self.timeWhenEstablished)>self.establishConnectionHold:
                        self.establishConnection()
		# calcuate CRC checksum and extract MSB and LSB 
		(high,low) = self.serialCalculateCRC(deviceData,len(deviceData))
		# consistency check between number of bytes sent and data array length
		if not nBytes == len(deviceData):
			print 'The number of bytes sent does not match the data array!'
			sys.exit(1)
		# create hex-string to be sent
		send = '16' + ID + '%0.2X' % nBytes
		# loop over length of data to be sent
		for i in range(len(deviceData)):
			send += '%0.2X' % deviceData[i]
		send += '%0.2X%0.2X' % (high,low)
		# convert hex string to bytes
		sendbytes = binascii.unhexlify(send)
		#
		if self.verbose:
		    print 'send', str(ID) , send, high, low
		nLoops = 0
		while True:
			# write bytes to interface
			self.timeWhenEstablished = time.time()
			self.ser.write(sendbytes)
			# wait
			time.sleep(self.sleepTime)
			# read answer from connection
			ansb = self.ser.read(nBytesRes)
			# compare answer with answer mask, if true: break, if false : redo
			if ansb[:len(response)] == response :
				if self.verbose:
                                        #print 'answer :', binascii.hexlify(ansb), len(ansb),
					print 'done'
				break
			if nLoops >= self.maxLoops:
				print 'Command was not successful!'
				break
			if self.verbose:
				print 'insufficient answer :', ansb, len(ansb),
			print '.',
			nLoops += 1
		return ansb
	##################################################################
	# initiates connection to SM5, note that the connection is lost after 3 sec
	def establishConnection(self):
		# establish connection before each command
		if self.verbose : 
			print 'Establish connection to SM5 . ',
		send = '16040000000000'
		sendbytes = binascii.unhexlify(send)
		while True:
			self.ser.write(sendbytes)
			time.sleep(self.sleepTime)
			ansConb = self.ser.read(6)
			if self.verbose:
				print ansConb
			if ansConb == '\x06\x04\x0b\x00\x00\x00':
				if self.verbose:
					print 'established'
				break
			print '.',
	#################################################################
	# list of implemented functions (add more functions here)
	def goSteps(self,device,axis,steps):
		IDcode = '0147'
		nBytes = 2
		response = '\x06\x04\x0b\x00\x00\x00'
		axisNumber = self.chooseAxis(device,axis)
		deviceData = ([axisNumber,steps])
		res = self.sendCommand(IDcode,nBytes,deviceData,response,len(response))
	def stepSlowDistance(self,device,axis,distance):
		IDcode = '013a'
		nBytes = 5
		response = '\x06\x04\x0b\x00\x00\x00'
		axisNumber = self.chooseAxis(device,axis)
		# convert float number to 4 byte in the standard IEEE format, give back hexadecimal
		dist_4hex = binascii.hexlify(struct.pack('>f',distance))
		# the float number has to be transmitted in reverse order  < LSB><Byte2><Byte3><MSB >
		# convert hex to int for CRC calculation
		deviceData = ([axisNumber,int(dist_4hex[6:],16),int(dist_4hex[4:6],16),int(dist_4hex[2:4],16),int(dist_4hex[:2],16)])
		res = self.sendCommand(IDcode,nBytes,deviceData,response,len(response))
	def goVariableFastToAbsolutePosition(self,device,axis,absPosition):
		IDcode = '0048'
		nBytes = 5
		response = '\x06\x04\x0b\x00\x00\x00'
		axisNumber = self.chooseAxis(device,axis)
		dist_4hex = binascii.hexlify(struct.pack('>f',absPosition))
		deviceData = ([axisNumber,int(dist_4hex[6:],16),int(dist_4hex[4:6],16),int(dist_4hex[2:4],16),int(dist_4hex[:2],16)])
		res = self.sendCommand(IDcode,nBytes,deviceData,response,len(response))
	def goVariableSlowToAbsolutePosition(self,device,axis,absPosition):
		IDcode = '0049'
		nBytes = 5
		response = '\x06\x04\x0b\x00\x00\x00'
		axisNumber = self.chooseAxis(device,axis)
		dist_4hex = binascii.hexlify(struct.pack('>f',absPosition))
		deviceData = ([axisNumber,int(dist_4hex[6:],16),int(dist_4hex[4:6],16),int(dist_4hex[2:4],16),int(dist_4hex[:2],16)])
		res = self.sendCommand(IDcode,nBytes,deviceData,response,len(response))
	def goVariableFastToRelativePosition(self,device,axis,relPosition):
		IDcode = '004a'
		nBytes = 5
		response = '\x06\x04\x0b\x00\x00\x00'
		axisNumber = self.chooseAxis(device,axis)
		dist_4hex = binascii.hexlify(struct.pack('>f',relPosition))
		deviceData = ([axisNumber,int(dist_4hex[6:],16),int(dist_4hex[4:6],16),int(dist_4hex[2:4],16),int(dist_4hex[:2],16)])
		res = self.sendCommand(IDcode,nBytes,deviceData,response,len(response))
	def goVariableSlowToRelativePosition(self,device,axis,relPosition):
		IDcode = '004b'
		nBytes = 5
		response = '\x06\x04\x0b\x00\x00\x00'
		axisNumber = self.chooseAxis(device,axis)
		dist_4hex = binascii.hexlify(struct.pack('>f',relPosition))
		deviceData = ([axisNumber,int(dist_4hex[6:],16),int(dist_4hex[4:6],16),int(dist_4hex[2:4],16),int(dist_4hex[:2],16)])
		res = self.sendCommand(IDcode,nBytes,deviceData,response,len(response))
	def stepIncrement(self,device,axis):
		IDcode = '0140'
		nBytes = 1
		response = '\x06\x04\x0b\x00\x00\x00'
		axisNumber = self.chooseAxis(device,axis)
		deviceData = ([axisNumber])
		res = self.sendCommand(IDcode,nBytes,deviceData,response,len(response))
	def stepDecrement(self,device,axis):
		IDcode = '0141'
		nBytes = 1
		response = '\x06\x04\x0b\x00\x00\x00'
		axisNumber = self.chooseAxis(device,axis)
		deviceData = ([axisNumber])
		res = self.sendCommand(IDcode,nBytes,deviceData,response,len(response))
	# remove current from the specified motor
	def switchOffAxis(self,device,axis):
		IDcode = '0034'
		nBytes = 1
		response = '\x06\x04\x0b\x00\x00\x00'
		axisNumber = self.chooseAxis(device,axis)
		deviceData = ([axisNumber])
		res = self.sendCommand(IDcode,nBytes,deviceData,response,len(response))
	def switchOnAxis(self,device,axis):
		IDcode = '0035'
		nBytes = 1
		response = '\x06\x04\x0b\x00\x00\x00'
		axisNumber = self.chooseAxis(device,axis)
		deviceData = ([axisNumber])
		res = self.sendCommand(IDcode,nBytes,deviceData,response,len(response))
	# zeros counter on specified axis
	def setAxisToZero(self,device,axis):
		IDcode = '00f0'
		nBytes = 1
		response = '\x06\x04\x0b\x00\x00\x00'
		axisNumber = self.chooseAxis(device,axis)
		deviceData = ([axisNumber])
		res = self.sendCommand(IDcode,nBytes,deviceData,response,len(response))
	# Queries position of specified axis.
	def getPosition(self,device,axis):
		IDcode = '0101'
		nBytes = 1
		response = '\x06\x00\x01\x04'
		axisNumber = self.chooseAxis(device,axis)
		deviceData = ([axisNumber])
		res = self.sendCommand(IDcode,nBytes,deviceData,response,10)
		return struct.unpack('f',res[4:8])[0]
	# Queries fast velocity of specified axis.
        def getPositioningVelocityFast(self,device,axis):
                IDcode = '0160'
                nBytes = 1
                response = '\x06\x00\x01\x02'
                axisNumber = self.chooseAxis(device,axis)
                deviceData = ([axisNumber])
                res = self.sendCommand(IDcode,nBytes,deviceData,response,8)
                return struct.unpack('H',res[4:6])[0]
        # Queries slow velocity of specified axis.
        def getPositioningVelocitySlow(self,device,axis):
                IDcode = '0161'
                nBytes = 1
                response = '\x06\x00\x01\x02'
                axisNumber = self.chooseAxis(device,axis)
                deviceData = ([axisNumber])
                res = self.sendCommand(IDcode,nBytes,deviceData,response,8)
                return struct.unpack('H',res[4:6])[0]
        # Queries fast velocity of specified axis.
        def setPositioningVelocityFast(self,device,axis,speed):
                IDcode = '003d'
                nBytes = 3
                response = '\x06\x04\x0b\x00\x00\x00'
                axisNumber = self.chooseAxis(device,axis)
                speed_2hex = binascii.hexlify(struct.pack('>H',speed))
                deviceData = ([axisNumber,int(speed_2hex[2:],16),int(speed_2hex[:2],16)])
                res = self.sendCommand(IDcode,nBytes,deviceData,response,len(response))
        # Queries slow velocity of specified axis.
        def setPositioningVelocitySlow(self,device,axis,speed):
                IDcode = '003c'
                nBytes = 3
                response = '\x06\x04\x0b\x00\x00\x00'
                axisNumber = self.chooseAxis(device,axis)
                speed_2hex = binascii.hexlify(struct.pack('>H',speed))
                deviceData = ([axisNumber,int(speed_2hex[2:],16),int(speed_2hex[:2],16)])
                res = self.sendCommand(IDcode,nBytes,deviceData,response,len(response))
        #########################################################
	# selects device and axis
	def chooseAxis(self,device,axis):
		if (device == 1):
			if axis=='x':
				deviceNumber = 1
			elif axis=='y':
				deviceNumber = 2
			elif axis=='z':
				deviceNumber = 3
			else:
				print 'Wrong axis for device', str(device), 'specified'
		elif (device == 2):
			if axis=='x':
				deviceNumber = 4
			elif axis=='y':
				deviceNumber = 5
			elif axis=='z':
				deviceNumber = 6
			else:
				print 'Wrong axis for device', str(device), 'specified'
		else:
			print 'Device number does not exist. Should be 1 or 2.'
		# 
		return deviceNumber
	#################################################
	# calculate CRC cecksum based on the data sent
	def serialCalculateCRC(self,butter,length):
		#
		crcPolynom = 0x1021
		crc = 0
		n = 0
		lll = length
		while (lll > 0):
			crc = crc ^ butter[n] << 8
			#print '1 ' , crc
			for i in arange(8):
				if (crc & 0x8000):
					crc = crc << 1 ^ crcPolynom
					#print 'if ',crc
				else:
					crc = crc << 1
					#print 'else ', crc
			lll -= 1
			n+=1
		#print "end while ",crc
		#print "after", crc , crc>>8 
		crcHigh = ctypes.c_ubyte(crc>>8)
		crcLow  = ctypes.c_ubyte(crc)
		return (crcHigh.value,crcLow.value)


	