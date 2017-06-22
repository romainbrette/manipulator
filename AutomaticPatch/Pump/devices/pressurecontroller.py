'''
A general pressure controller class
'''
all = ['PressureController']

class PressureController(object):
    def __init__(self):
        pass

    def measure(self, port = 0):
        '''
        Measures the instantaneous pressure, on designated port.
        '''
        pass

    def set_pressure(self, pressure, port = 0):
        '''
        Sets the pressure, on designated port.
        '''
        pass