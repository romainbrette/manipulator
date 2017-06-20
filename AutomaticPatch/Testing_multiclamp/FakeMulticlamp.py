"""
Fake multiclamp class in case no multiclamp is connected
"""

import ctypes


class FakeMultiClamp(object):
    """
    Fake device representing a MultiClamp amplifer channel (i.e., one amplifier with
    two channels is represented by two devices).
    Does absolutly nothing.

    """

    def __init__(self, **kwds):
        self.fast_comp = ctypes.c_float(0.)
        self.slow_comp = ctypes.c_float(0.)
        self.pulse_amp = ctypes.c_float(0.)
        self.pulse_dur = ctypes.c_float(0.)
        self.freq_pulse_amp = ctypes.c_float(0.)
        self.freq_pulse_freq = ctypes.c_float(0.)
        self.meter_resist_en = ctypes.c_bool(False)
        self.leak_val = ctypes.c_float(0.0)
        self.primary_memcur = ctypes.c_bool(False)
        self.meter_val = ctypes.c_float(0.)
        pass

    def voltage_clamp(self):
        pass

    def current_clamp(self):
        pass

    def get_fast_compensation_capacitance(self):
        return self.fast_comp

    def set_fast_compensation_capacitance(self, capacitance):
        self.fast_comp = ctypes.c_float(capacitance)
        pass

    def auto_fast_compensation(self):
        pass

    def get_slow_compensation_capacitance(self):
        return self.slow_comp

    def set_slow_compensation_capacitance(self, capacitance):
        self.slow_comp = ctypes.c_float(capacitance)
        pass

    def auto_slow_compensation(self):
        pass

    def pulse(self):
        pass

    def set_pulse_amplitude(self, amplitude):
        self.pulse_amp = ctypes.c_float(amplitude)
        pass

    def get_pulse_amplitude(self):
        return self.pulse_amp

    def set_pulse_duration(self, duration):
        self.pulse_dur = ctypes.c_float(duration)
        pass

    def get_pulse_duration(self):
        return self.pulse_dur

    def freq_pulse_enable(self, enable):
        pass

    def set_freq_pulse_amplitude(self, amplitude):
        self.freq_pulse_amp = ctypes.c_float(amplitude)
        pass

    def get_freq_pulse_amplitude(self):
        return self.freq_pulse_amp
    
    def set_freq_pulse_frequency(self, frequency):
        self.freq_pulse_freq = ctypes.c_float(frequency)
        pass

    def get_freq_pulse_frequency(self):
        return self.freq_pulse_freq
    
    def meter_resist_enable(self, enable):
        self.meter_resist_en = ctypes.c_bool(enable)
        pass
    
    def get_meter_resist_enable(self):
        return self.meter_resist_en
    
    def set_leak_comp_enable(self, enable):
        pass
    
    def get_leak_res(self):
        return self.leak_val
    
    def auto_leak_res(self):
        pass
    
    def set_primary_signal_membcur(self):
        self.primary_memcur = ctypes.c_bool(True)
        pass
    
    def get_primary_signal_membcur(self):
        return self.primary_memcur

    def set_primary_signal_gain(self, gain):
        pass
    
    def set_primary_signal_lpf(self, lpf):
        pass
    
    def set_primary_signal_hpf(self, hpf):
        pass
    
    def set_secondary_signal_membpot(self):
        pass
    
    def get_secondary_signal_membpot(self):
        pass

    def set_secondary_signal_lpf(self, lpf):
        pass
    
    def set_secondary_signal_gain(self, gain):
        pass

    def auto_pipette_offset(self):
        pass

    def get_meter_value(self):
        return self.meter_val

    def close(self):
        pass


if __name__ == '__main__':
    import time
    from matplotlib.pyplot import *

    val = []
    print('Connecting to the MultiClamp amplifier')
    mcc = FakeMultiClamp(channel=1)
    print('Switching to voltage clamp')
    mcc.voltage_clamp()
    print('Running automatic slow compensation')
    mcc.auto_slow_compensation()
    print('Running automatic fast compensation')
    mcc.auto_fast_compensation()
    print('Compensation values:')
    print('Slow: {}'.format(mcc.get_slow_compensation_capacitance()))
    print('Fast: {}'.format(mcc.get_fast_compensation_capacitance()))
    mcc.set_freq_pulse_amplitude(1e-2)
    mcc.set_freq_pulse_frequency(1e-3)
    mcc.set_pulse_amplitude(1e-2)
    mcc.set_pulse_duration(1e-2)
    mcc.set_primary_signal_membcur()
    mcc.set_primary_signal_lpf(2000)
    mcc.set_secondary_signal_membpot()
    mcc.set_secondary_signal_lpf(2000)
    time.sleep(.5)
    mcc.auto_pipette_offset()
    mcc.meter_resist_enable(True)
    mcc.freq_pulse_enable(True)
    init = time.time()
    while time.time() - init < 1:
        val += [mcc.get_meter_value().value]
    # print time.time()*1000 - init
    print min(val)
    print max(val)
    print np.median(val)
    plot(val)
    mcc.meter_resist_enable(False)
    mcc.freq_pulse_enable(False)
    mcc.meter_resist_enable(False)
    mcc.close()
    show()
