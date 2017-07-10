from PumpClass import *

__all__ = ['FakePump']


class FakePump(PumpClass):

    def __init__(self):
        PumpClass.__init__(self)
        self.val = 0.
        pass

    def measure(self):
        return self.val

    def set_pressure(self, pressure):
        self.val = pressure
        pass
