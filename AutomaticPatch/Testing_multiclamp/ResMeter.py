from devices import *
import nidaqmx
from math import fabs
import time
from threading import Thread, RLock
import numpy as np


class ResistanceMeter(Thread):

    def __init__(self):

        Thread.__init__(self)
        print('Connecting to the MultiClamp amplifier')
        self.mcc = MultiClamp(channel=1)
        print('Switching to voltage clamp')
        self.mcc.voltage_clamp()
        print('Running automatic slow compensation')
        self.mcc.auto_slow_compensation()
        print('Running automatic fast compensation')
        self.mcc.auto_fast_compensation()

        self.mcc.meter_resist_enable(False)

        self.mcc.set_freq_pulse_amplitude(1e-2)
        self.mcc.set_freq_pulse_frequency(1e-3)
        self.mcc.freq_pulse_enable(False)

        self.mcc.set_primary_signal_membcur()
        self.mcc.set_primary_signal_lpf(2000)
        self.mcc.set_primary_signal_gain(5)
        self.mcc.set_secondary_signal_membpot()
        self.mcc.set_secondary_signal_lpf(2000)
        self.mcc.set_secondary_signal_gain(5)
        time.sleep(1)

        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
            task.ai_channels.add_ai_voltage_chan("Dev1/ai1")
            self.init = task.read()

        self.mcc.auto_pipette_offset()
        self.acquisition = True
        self.continious = False
        self.discrete = False
        self.res = None

    def run(self):
        while self.acquisition:
            lock = RLock()
            lock.acquire()

            if self.continious:

                self.mcc.freq_pulse_enable(True)
                while self.continious:
                    with nidaqmx.Task() as task:

                        res = []
                        task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
                        task.ai_channels.add_ai_voltage_chan("Dev1/ai1")

                        for _ in range(3):
                            temp = task.read(number_of_samples_per_channel=100)
                            res += [fabs((np.mean(temp[1]) / 10.) / (1e-9 * np.mean(temp[0]) / 0.5))]
                        self.res = np.median(res)

                self.mcc.freq_pulse_enable(False)

            elif self.discrete:

                self.mcc.freq_pulse_enable(True)
                with nidaqmx.Task() as task:
                    self.res = []
                    task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
                    task.ai_channels.add_ai_voltage_chan("Dev1/ai1")

                    for _ in range(3):
                        temp = task.read(number_of_samples_per_channel=100)
                        self.res += [fabs((np.mean(temp[1]) / 10.) / (1e-9 * np.mean(temp[0]) / 0.5))]

                    self.res = np.median(self.res)

                self.mcc.freq_pulse_enable(False)
                self.discrete = False

            else:
                pass

            lock.release()

    def get_res(self):

        res = []

        self.mcc.freq_pulse_enable(True)
        init_time = int(round(time.time() * 1000))

        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
            task.ai_channels.add_ai_voltage_chan("Dev1/ai1")
            for _ in range(3):
                temp = task.read(number_of_samples_per_channel=100)
                res += [fabs((np.mean(temp[1])/10.)/(1e-9*np.mean(temp[0])/0.5))]

        self.mcc.freq_pulse_enable(False)
        print('Time: {}ms'.format(int(round(time.time() * 1000))-init_time))
        return np.mean(res)

    def stop(self):
        self.continious = False
        self.acquisition = False
        time.sleep(.2)

    def start_continious_acquisition(self):
        self.continious = True
        self.discrete = False
        time.sleep(.2)

    def stop_continious_acquisition(self):
        self.continious = False
        self.discrete = False
        time.sleep(.2)

    def get_discrete_acquisition(self):
        self.continious = False
        self.discrete = True
        time.sleep(.2)

    def __del__(self):
        self.stop()
        self.mcc.close()


if __name__ == '__main__':
    from matplotlib.pyplot import *
    val = []
    multi = ResistanceMeter()
    multi.start()
    multi.start_continious_acquisition()
    print('Getting resistance')
    init = time.time()
    while time.time() - init < 5:
        val += [multi.res]
    multi.stop_continious_acquisition()
    multi.stop()
    print min(val)
    print max(val)
    print np.median(val)
    plot(val)
    show()
    del multi
