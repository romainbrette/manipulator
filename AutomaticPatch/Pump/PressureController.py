from ob1 import *
from FakeOB import *
from time import sleep


class PressureController(OB1, FakeOB1):

    def __init__(self):
        try:
            OB1.__init__(self)
        except (AttributeError, RuntimeError):
            FakeOB1.__init__(self)

        self.release()
    pass

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
        self.set_pressure(0)
        # -15 to -20 in Kodandaramaiah paper?

    def break_in(self):
        # Breaks in with a ramp
        # Holst thesis: 0 to -345 mBar in 1.5 second
        # Desai: -150 mBar for 1 second; repeated attempts
        self.set_pressure(-150)
        sleep(1)
        self.release()
