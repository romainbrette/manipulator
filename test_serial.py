'''
Testing manipulator control
'''
from devices import *
import struct
import time

d = LuigsNeumann_SM10()

x = d.position(1)
y = d.position(2)
print x,y
d.move(1, x+200.)
d.move(2, y+200.)
print d.position(1),d.position(2)
time.sleep(1)
print d.position(1),d.position(2)
time.sleep(1)
print d.position(1),d.position(2)
