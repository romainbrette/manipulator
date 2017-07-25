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
        """
        Set the amplifier in voltage clamp mode
        :return: 
        """
        pass

    def current_clamp(self):
        """
        set the amplifier in current clamp mode
        :return: 
        """
        pass

    def null_current(self):
        """
        set the amplifier in i=0 mode
        :return: 
        """
        pass

    def get_fast_compensation_capacitance(self):
        """
        Get fast compensation capacitance of pipette circuit
        :return: 
        """
        return self.fast_comp

    def set_fast_compensation_capacitance(self, capacitance):
        """
        set fast compensation capacitance of pipette circuit
        :param capacitance: 
        :return: 
        """
        self.fast_comp = capacitance
        pass

    def auto_fast_compensation(self):
        """
        Set fast compensation of pipette automatically
        :return: 
        """
        pass

    def get_slow_compensation_capacitance(self):
        """
        Get slow compensation capacitance of pipette circuit
        :return: 
        """
        return self.slow_comp

    def set_slow_compensation_capacitance(self, capacitance):
        """
        Set slow compensation capacitance of pipette circuit
        :param capacitance: 
        :return: 
        """
        self.slow_comp = capacitance
        pass

    def auto_slow_compensation(self):
        """
        Set slow compensation of pipette automatically
        :return: 
        """
        pass

    def pulse(self):
        """
        Execute one pulse
        :return: 
        """
        pass

    def set_pulse_amplitude(self, amplitude):
        """
        Set amplitude of pulse (in V)
        :param amplitude: 
        :return: 
        """
        self.pulse_amp = amplitude
        pass

    def get_pulse_amplitude(self):
        """
        get amplitude of pulse (in V)
        :return: 
        """
        return self.pulse_amp

    def set_pulse_duration(self, duration):
        """
        Set duration of pulse in second
        :param duration: 
        :return: 
        """
        self.pulse_dur = duration
        pass

    def get_pulse_duration(self):
        """
        Get duration of pulse in second
        :return: 
        """
        return self.pulse_dur

    def freq_pulse_enable(self, enable):
        """
        Enable/Disable pulse emission (different from pulse)
        :param enable: 
        :return: 
        """
        pass

    def set_freq_pulse_amplitude(self, amplitude):
        """
        Set the amplitude of pulse emission
        :param amplitude: 
        :return: 
        """
        self.freq_pulse_amp = amplitude
        pass

    def get_freq_pulse_amplitude(self):
        """
        Get the amplitude of pulse emission
        :return: 
        """
        return self.freq_pulse_amp

    def set_freq_pulse_frequency(self, frequency):
        """
        Set the frequency of pulse emission
        :param frequency: 
        :return: 
        """
        self.freq_pulse_freq = frequency
        pass

    def get_freq_pulse_frequency(self):
        """
        Get the frequency of pulse emission
        :return: 
        """
        return self.freq_pulse_freq

    def meter_resist_enable(self, enable):
        """
        Enable/disable resistance metering
        :param enable: 
        :return: 
        """
        self.meter_resist_en = enable
        pass

    def get_meter_resist_enable(self):
        """
        Get the state of resistance metering (Enable or Disable)
        :return: 
        """
        return self.meter_resist_en

    def set_leak_comp_enable(self, enable):
        """
        Enable/disable leak compensation
        :param enable: 
        :return: 
        """
        pass

    def get_leak_res(self):
        """
        Get the resistance value of leak compensation
        :return: 
        """
        return self.leak_val

    def auto_leak_res(self):
        """
        Automatically compensate leak resistance
        :return: 
        """
        pass

    def set_primary_signal_membcur(self):
        """
        Set primary signal output as the membrane current
        :return: 
        """
        self.primary_memcur = True
        pass

    def get_primary_signal(self):
        """
        Get the state of primary signal
        :return: 
        """
        return self.primary_memcur

    def set_primary_signal_gain(self, gain):
        """
        Set the gain of primary signal output (membrane current, potential...)
        :param gain: 
        :return: 
        """
        pass

    def set_primary_signal_lpf(self, lpf):
        """
        Set the cutoff frequency of the low pass filter of the primary signal output
        :param lpf: Cutoff frequency in Hertz
        :return: 
        """
        pass

    def set_primary_signal_hpf(self, hpf):
        """
        Set the cutoff frequency of the high pass filter of the primary signal output
        :param hpf: Cutoff frequency in Hertz
        :return: 
        """
        pass

    def set_secondary_signal_membpot(self):
        """
        Set the secondary signal output as membrane potential
        :return: 
        """
        pass

    def get_secondary_signal(self):
        """
        Get the state of the secondary signal output (membrane current, potential...)
        :return: 
        """
        pass

    def set_secondary_signal_lpf(self, lpf):
        """
        Set the cutoff frequency of the low pass filter of the secondary signal output
        :param lpf: Cutoff frequency in Hertz
        :return: 
        """
        pass

    def set_secondary_signal_gain(self, gain):
        """
        Set the gain of secondary signal output (membrane current, potential...)
        :param gain: 
        :return: 
        """
        pass

    def auto_pipette_offset(self):
        """
        Launch automatic pipette offset
        :return: 
        """
        pass

    def get_meter_value(self):
        """
        Get the meter value (resistance if resistance meter enable, potential otherwise)
        :return: 
        """
        return self.meter_val

    def set_holding_enable(self, enable):
        """
        Enable/disable holding
        :param enable: 
        :return: 
        """
        pass

    def set_holding(self, value):
        """
        Set holding
        :param value: holding potential (in mV) 
        :return: 
        """
        self.holding = value
        pass

    def zap(self):
        """
        Send a zap
        :return: 
        """
        pass

    def set_zap_duration(self, duration):
        """
        Set the duration of the zap
        :param duration: 
        :return: 
        """
        pass

    def close(self):
        pass

