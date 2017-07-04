from pump_devices import *


class Pump(object):

    def __init__(self, pumpclass='FakePump'):
        try:
            if pumpclass == 'OB1':
                self.controller = OB1()
            elif pumpclass == 'FakePump':
                self.controller = FakePump()
            else:
                raise AttributeError
        except (AttributeError, RuntimeError):
            self.pump = FakePump()

    def set_pressure(self, value):
        self.controller.set_pressure(value)

    def measure(self):
        return self.controller.measure()
