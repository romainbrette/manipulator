from devices import *
import nidaqmx
from math import fabs
import time
from threading import Thread, RLock
import numpy as np


class ResistanceMeter:

    def __init__(self):

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
        self.mcc.set_freq_pulse_frequency(1e-2)
        self.mcc.freq_pulse_enable(False)

        self.mcc.set_primary_signal_membcur()
        self.mcc.set_primary_signal_lpf(1000)
        self.mcc.set_primary_signal_gain(5)
        self.mcc.set_secondary_signal_membpot()
        self.mcc.set_secondary_signal_lpf(1000)
        self.mcc.set_secondary_signal_gain(5)
        time.sleep(1)

        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
            task.ai_channels.add_ai_voltage_chan("Dev1/ai1")
            self.init = task.read()

        self.mcc.auto_pipette_offset()
        self.continious = None

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

    def start_continious_meter(self):
        self.continious = ContinuousMeter(self.mcc)
        self.continious.start()

    def stop_continious_meter(self):
        try:
            self.continious.stop()
        except AttributeError:
            print('Continious metering has not been started.')

    def get_continious_meter_res(self):
        try:
            out = self.continious.res
            return out
        except AttributeError:
            print('Continious metering has not been started.')

    def __del__(self):
        self.mcc.close()


class ContinuousMeter(Thread):

    def __init__(self, mcc):
        Thread.__init__(self)
        self.meter = True
        self.multi = mcc
        self.res = None

    def run(self):
        self.multi.freq_pulse_enable(True)
        while self.meter:
            with nidaqmx.Task() as task, RLock():
                self.res = []
                task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
                task.ai_channels.add_ai_voltage_chan("Dev1/ai1")
                for _ in range(3):
                    temp = task.read(number_of_samples_per_channel=100)
                    self.res += [fabs((np.mean(temp[1])/10.)/(1e-9*np.mean(temp[0])/0.5))]
                self.res = np.mean(self.res)
        self.multi.freq_pulse_enable(False)

    def stop(self):
        self.meter = False


if __name__ == '__main__':
    from matplotlib.pyplot import *
    val = []
    multi = ResistanceMeter()
    print('Getting resistance')
    val += [multi.get_res()]

    print min(val)
    print max(val)
    print np.median(val)
    plot(val)
    # show()
    del multi
