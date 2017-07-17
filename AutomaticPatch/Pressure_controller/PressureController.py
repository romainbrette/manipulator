from os.path import expanduser
from time import sleep
from numpy import savetxt, array
from Pump import *

home = expanduser("~")
filename = home+'/pressure.txt'


class PressureController(Pump):
    """
    Pressure controller for patch clamp
    """

    def __init__(self, pressure_controller=None):
        Pump.__init__(self, pressure_controller)

        self.isrecording = False
        self.measurement = list()

        # Begin at 0mBar
        self.release()
        pass

    def high_pressure(self):
        """
        High pressure output, 800mBar
        :return: 
        """
        self.set_pressure(800)

    def nearing(self):
        """ 
        Small pressure (25mBar) so pipette does not get obstructed
        :return: 
        """
        self.set_pressure(30)  # mBar (25-30)

    def seal(self):
        """
        Sealing with small negative pressure: -25mBar
        :return: 
        """
        self.set_pressure(-30)   # (from Desai)
        # -15 to -20 in Kodandaramaiah paper?

    def release(self):
        """
        Release the pressure
        :return: 
        """
        self.set_pressure(0)
        # -15 to -20 in Kodandaramaiah paper?

    def break_in(self):
        """
        Breaks in with a ramp: 150 mBar for 1 sec
        :return: 
        """
        # Holst thesis: 0 to -345 mBar in 1.5 second
        # Desai: -150 mBar for 1 second; repeated attempts
        self.set_pressure(-150)
        sleep(1)
        self.release()

    def record(self):
        """
        Record pressure, save it in file when called again
        :return: 
        """
        self.isrecording ^= 1
        if self.isrecording:
            # Here we start clocked recording using a timer - could be different depending on the interface
            self.sample()  # 20 Hz recording
        else:
            # Save to while when it's finished
            savetxt(filename, array(self.measurement))

    def sample(self):
        """
        Take a measure of pressure until record is called again
        :return: 
        """
        if self.isrecording:
            pressure = self.measure()
            self.measurement.append(pressure)
            sleep(0.05)
            self.sample()

if __name__ == '__main__':
    pressure_controler = PressureController()
    pressure_controler.record()
    sleep(5)
    pressure_controler.record()
