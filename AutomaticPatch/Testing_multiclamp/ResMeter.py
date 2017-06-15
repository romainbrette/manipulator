from devices import *
import nidaqmx
from math import fabs
import time
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

    def get_res(self):

        n = 0
        res = []

        self.mcc.freq_pulse_enable(True)
        init_time = int(round(time.time() * 1000))

        with nidaqmx.Task() as task, nidaqmx.Task() as output:
            task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
            task.ai_channels.add_ai_voltage_chan("Dev1/ai1")
            output.ao_channels.add_ao_voltage_chan('Dev1/ao0')
            n = 0
            while n<3:
                temp = task.read(number_of_samples_per_channel=100)
                res += [fabs((np.mean(temp[1])/10.)/(1e-9*np.mean(temp[0])/0.5))]
                n += 1

        self.mcc.freq_pulse_enable(False)
        print('Time: {}ms'.format(int(round(time.time() * 1000))-init_time))
        return np.mean(res)

    def __del__(self):
        self.mcc.close()

if __name__ == '__main__':
    from matplotlib.pyplot import *
    val =[]
    multi = ResistanceMeter()
    print('Getting resistance')
    val += [multi.get_res()]

    print min(val)
    print max(val)
    print np.median(val)
    plot(val)
    #show()
    del multi
