from pump_devices import *


class Pump(object):
    """
    Connect to the desired pump for pressure control
    """

    def __init__(self, pumpclass='FakePump'):
        try:
            if pumpclass == 'OB1':
                self.controller = OB1()
            elif pumpclass == 'FakePump':
                self.controller = FakePump()
            else:
                raise AttributeError
        except (AttributeError, RuntimeError):
            # Unkown pump or failed to connect
            self.controller = FakePump()

    def set_pressure(self, value):
        """
        Set the output pressure at desired value in mBar
        :param value: pressure in mBar
        :return: 
        """
        self.controller.set_pressure(value)

    def measure(self):
        """
        Measure the pressure, once, in mBar
        :return: 
        """
        return self.controller.measure()
