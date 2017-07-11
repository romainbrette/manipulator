import numpy as np
from Amplifier import *
from time import sleep, time
from threading import Thread

__all__ = ['ResistanceMeter']


class ResistanceMeter(Thread, Amplifier):
    """
    Amplifier to meter the resistance
    """

    def __init__(self, amplifier):

        # init thread and amplifier
        Thread.__init__(self)
        Amplifier.__init__(self, amplifier)

        # Set in voltage clamp
        self.voltage_clamp()

        # Disable resistance metering (because of pulses)
        self.meter_resist_enable(False)

        # Disable pulses
        self.freq_pulse_enable(False)

        # compensate pipette eletronical circuit
        self.auto_slow_compensation()
        self.auto_fast_compensation()

        # Set pulse frequency and amplitude
        self.set_freq_pulse_amplitude(1e-2)
        self.set_freq_pulse_frequency(1e-2)

        # Boolean for type of metering
        self.acquisition = True
        self.continuous = False
        self.discrete = False

        # resistance measured
        self.res = 0.

        # Potential measured
        self.pot = 0.

        # start thread
        self.start()
        pass

    def run(self):
        """
        Thread runs for getting resistance
        :return: 
        """
        while self.acquisition:
            # acquisition On
            if self.continuous:
                # Continuous acquisition
                while self.continuous:
                    if self.get_meter_resist_enable():
                        # Resistance
                        self.res = self.get_meter_value()
                    else:
                        # Potential
                        self.pot = self.get_meter_value()
            elif self.discrete:
                # Single acquisition
                if self.get_meter_resist_enable():
                    # Resistance
                    self.res = self.get_meter_value()
                else:
                    # Potential
                    self.pot = self.get_meter_value()
                self.discrete = False

            else:
                pass
        # End of thread
        self.set_holding_enable(False)

    def stop(self):
        """
        Stop the thread
        :return: 
        """
        self.continuous = False
        self.acquisition = False
        sleep(.2)

    def start_continuous_acquisition(self):
        """
        Start metering continuously
        :return: 
        """
        self.continuous = True
        self.discrete = False
        sleep(.2)

    def stop_continuous_acquisition(self):
        """
        Stop metering continuously
        :return: 
        """
        self.continuous = False
        self.discrete = False
        sleep(.2)

    def get_discrete_acquisition(self):
        """
        Get a single resistance measure
        :return: 
        """
        self.continuous = False
        self.discrete = True
        sleep(.2)

    def __del__(self):
        self.stop()
        self.close()


if __name__ == '__main__':
    from matplotlib.pyplot import *
    val = []
    multi = ResistanceMeter('Multiclamp')
    multi.start_continuous_acquisition()
    print('Getting resistance')
    init = time()
    while time() - init < 5:
        val += [multi.res]
    multi.stop_continuous_acquisition()
    multi.stop()
    print min(val)
    print max(val)
    print np.median(val)
    plot(val)
    show()
    del multi
