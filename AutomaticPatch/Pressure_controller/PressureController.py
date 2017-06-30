from os.path import expanduser
from time import sleep
from numpy import savetxt, array
from pump_devices import *

home = expanduser("~")
filename = home+'/pressure.txt'


class PressureController(object):

    def __init__(self, pressure_controller=None):
        try:
            if pressure_controller == 'OB1':
                self.controller = OB1()
            else:
                raise AttributeError
        except (AttributeError, RuntimeError):
            self.controller = FakePump()

        self.isrecording = False
        self.measurement = list()
        self.release()
    pass

    def set_pressure(self, value):
        self.controller.set_pressure(value)

    def measure(self):
        return self.controller.measure()

    def high_pressure(self):
        self.set_pressure(800)

    def nearing(self):
        self.set_pressure(25)  # mBar (25-30)

    def seal(self):
        # Sealing with small negative pressure
        self.set_pressure(-25)   # (from Desai)
        # -15 to -20 in Kodandaramaiah paper?

    def release(self):
        # Release the pressure
        self.controller.set_pressure(0)
        # -15 to -20 in Kodandaramaiah paper?

    def break_in(self):
        # Breaks in with a ramp
        # Holst thesis: 0 to -345 mBar in 1.5 second
        # Desai: -150 mBar for 1 second; repeated attempts
        self.controller.set_pressure(-150)
        sleep(1)
        self.release()

    def record(self):
        self.isrecording = not self.isrecording
        if self.isrecording:
            # Here we start clocked recording using a timer - could be different depending on the interface
            self.sample()  # 20 Hz recording
        else:
            # Save to while when it's finished
            savetxt(filename, array(self.measurement))

    def sample(self):
        if self.isrecording:
            pressure = self.measure()
            print pressure
            self.measurement.append(pressure)
            sleep(0.05)
            self.sample()

if __name__ == '__main__':
    pressure_controler = PressureController()
    pressure_controler.record()
    sleep(5)
    pressure_controler.record()
