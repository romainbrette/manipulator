from pylab import *

t,x,y = loadtxt('tracking.txt').T

plot(x,y,'.')
show()
