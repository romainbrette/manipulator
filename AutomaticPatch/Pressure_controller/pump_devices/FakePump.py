from PumpClass import *

__all__ = ['FakePump']


class FakePump(PumpClass):
    """
    Fake pump in case pressure controls are not wanted or connection to desired pump failed
    """

    def __init__(self):
        PumpClass.__init__(self)
        self.val = 0.
        pass

    def measure(self):
        return self.val

    def set_pressure(self, pressure):
        self.val = pressure
        pass
