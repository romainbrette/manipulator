import numpy as np
from Amplifier import *
from time import sleep, time
from threading import Thread

__all__ = ['ResistanceMeter']


class ResistanceMeter(Thread, Amplifier):

    def __init__(self, amplifier):

        Thread.__init__(self)
        Amplifier.__init__(self, amplifier)
        self.voltage_clamp()
        self.auto_slow_compensation()
        self.auto_fast_compensation()

        self.meter_resist_enable(False)

        self.set_freq_pulse_amplitude(1e-2)
        self.set_freq_pulse_frequency(1e-2)
        self.freq_pulse_enable(False)

        self.acquisition = True
        self.continuous = False
        self.discrete = False
        self.res = 0.

        self.start()
        pass

    def run(self):
        while self.acquisition:
            if self.get_meter_resist_enable():
                if self.continuous:

                    self.freq_pulse_enable(True)
                    while self.continuous:

                        res = []

                        for _ in range(3):
                            res += [self.get_meter_value()]
                        self.res = np.mean(res)

                    self.freq_pulse_enable(False)

                elif self.discrete:

                    self.freq_pulse_enable(True)
                    res = []

                    for _ in range(3):

                        res += [self.get_meter_value()]

                    self.res = np.mean(res)

                    self.freq_pulse_enable(False)
                    self.discrete = False

                else:
                    pass
            else:
                self.res = 0.
        self.set_holding_enable(False)

    def stop(self):
        self.continuous = False
        self.acquisition = False
        sleep(.2)

    def start_continuous_acquisition(self):
        self.continuous = True
        self.discrete = False
        sleep(.2)

    def stop_continuous_acquisition(self):
        self.continuous = False
        self.discrete = False
        sleep(.2)

    def get_discrete_acquisition(self):
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
