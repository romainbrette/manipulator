__all__ = ['AmplifierClass']


class AmplifierClass(object):
    """
    Base class for making your own subclass to control your amplifier 
    and ensure full compatibility with the other scripts.
    Do not forget to update the __init__.py of the 'amp_devices' for further import.
    """
    def __init__(self):
        self.fast_comp = 0.
        self.slow_comp = 0.
        self.pulse_amp = 0.
        self.pulse_dur = 0.
        self.freq_pulse_amp = 0.
        self.freq_pulse_freq = 0.
        self.meter_resist_en = False
        self.leak_val = 0.
        self.primary_memcur = False
        self.meter_val = 0.
        self.holding = 0.
        pass

    def voltage_clamp(self):
        pass

    def current_clamp(self):
        pass

    def get_fast_compensation_capacitance(self):
        return self.fast_comp

    def set_fast_compensation_capacitance(self, capacitance):
        self.fast_comp = capacitance
        pass

    def auto_fast_compensation(self):
        pass

    def get_slow_compensation_capacitance(self):
        return self.slow_comp

    def set_slow_compensation_capacitance(self, capacitance):
        self.slow_comp = capacitance
        pass

    def auto_slow_compensation(self):
        pass

    def pulse(self):
        pass

    def set_pulse_amplitude(self, amplitude):
        self.pulse_amp = amplitude
        pass

    def get_pulse_amplitude(self):
        return self.pulse_amp

    def set_pulse_duration(self, duration):
        self.pulse_dur = duration
        pass

    def get_pulse_duration(self):
        return self.pulse_dur

    def freq_pulse_enable(self, enable):
        pass

    def set_freq_pulse_amplitude(self, amplitude):
        self.freq_pulse_amp = amplitude
        pass

    def get_freq_pulse_amplitude(self):
        return self.freq_pulse_amp

    def set_freq_pulse_frequency(self, frequency):
        self.freq_pulse_freq = frequency
        pass

    def get_freq_pulse_frequency(self):
        return self.freq_pulse_freq

    def meter_resist_enable(self, enable):
        self.meter_resist_en = enable
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
        self.primary_memcur = True
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

    def set_holding_enable(self, enable):
        pass

    def set_holding(self, value):
        self.holding = value
        pass

    def close(self):
        pass

