import numpy as np
from FakeMulticlamp import *
from MultiClamp import *
from time import sleep
from threading import Thread

__all__ = ['ResistanceMeter']


class ResistanceMeter(Thread):

    def __init__(self):

        Thread.__init__(self)
        print('Connecting to the MultiClamp amplifier')
        try:
            self.amp = MultiClamp(channel=1)
        except (AttributeError, RuntimeError):
            print 'No multiclamp detected, switching to fake amplifier.'
            self.amp = FakeMultiClamp()
        print('Switching to voltage clamp')
        self.amp.voltage_clamp()
        print('Running automatic slow compensation')
        self.amp.auto_slow_compensation()
        print('Running automatic fast compensation')
        self.amp.auto_fast_compensation()

        self.amp.meter_resist_enable(False)

        self.amp.set_freq_pulse_amplitude(1e-2)
        self.amp.set_freq_pulse_frequency(1e-2)
        self.amp.freq_pulse_enable(False)

        self.acquisition = True
        self.continuous = False
        self.discrete = False
        self.res = 0.

    def run(self):
        while self.acquisition:
            if self.amp.get_meter_resist_enable().value:
                if self.continuous:

                    self.amp.freq_pulse_enable(True)
                    while self.continuous:

                        res = []

                        for _ in range(3):
                            res += [self.amp.get_meter_value().value]
                        self.res = np.mean(res)

                    self.amp.freq_pulse_enable(False)

                elif self.discrete:

                    self.amp.freq_pulse_enable(True)
                    res = []

                    for _ in range(3):

                        res += [self.amp.get_meter_value().value]

                    self.res = np.mean(res)

                    self.amp.freq_pulse_enable(False)
                    self.discrete = False

                else:
                    pass
            else:
                self.res = 0.
        self.amp.set_holding_enable(False)

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
        self.amp.close()


if __name__ == '__main__':
    from matplotlib.pyplot import *
    val = []
    multi = ResistanceMeter()
    multi.start()
    multi.start_continuous_acquisition()
    print('Getting resistance')
    init = time.time()
    while time.time() - init < 5:
        val += [multi.res]
    multi.stop_continuous_acquisition()
    multi.stop()
    print min(val)
    print max(val)
    print np.median(val)
    plot(val)
    show()
    del multi
