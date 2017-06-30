"""
Amplifier class that connects to amplifier or switch to a fake one if none is found. 
"""
from amp_devices import *

__all__ = ['Amplifier']


class Amplifier(object):
    """
    Connects to the amplifier
    """

    def __init__(self, amplifier=None, **kwargs):
        try:
            if amplifier == 'Multiclamp':
                self.amp = MultiClamp(channel=1)
            else:
                raise AttributeError
        except (AttributeError, RuntimeError):
            print 'No multiclamp detected, switching to fake amplifier.'
            self.amp = FakeAmplifier()
        pass

    def voltage_clamp(self):
        self.amp.voltage_clamp()
        pass

    def current_clamp(self):
        self.amp.current_clamp()
        pass

    def get_fast_compensation_capacitance(self):
        return self.get_fast_compensation_capacitance()

    def set_fast_compensation_capacitance(self, capacitance):
        self.amp.set_fast_compensation_capacitance(capacitance)
        pass

    def auto_fast_compensation(self):
        self.amp.auto_fast_compensation()
        pass

    def get_slow_compensation_capacitance(self):
        return self.amp.get_slow_compensation_capacitance()

    def set_slow_compensation_capacitance(self, capacitance):
        self.amp.set_slow_compensation_capacitance(capacitance)
        pass

    def auto_slow_compensation(self):
        self.amp.auto_slow_compensation()
        pass

    def pulse(self):
        self.amp.pulse()
        pass

    def set_pulse_amplitude(self, amplitude):
        self.amp.set_pulse_amplitude(amplitude)
        pass

    def get_pulse_amplitude(self):
        return self.amp.get_pulse_amplitude()

    def set_pulse_duration(self, duration):
        self.amp.set_pulse_duration(duration)
        pass

    def get_pulse_duration(self):
        return self.amp.get_pulse_duration()

    def freq_pulse_enable(self, enable):
        self.amp.freq_pulse_enable(enable)
        pass

    def set_freq_pulse_amplitude(self, amplitude):
        self.amp.set_freq_pulse_amplitude(amplitude)
        pass

    def get_freq_pulse_amplitude(self):
        return self.amp.get_freq_pulse_amplitude()

    def set_freq_pulse_frequency(self, frequency):
        self.amp.set_freq_pulse_frequency(frequency)
        pass

    def get_freq_pulse_frequency(self):
        return self.amp.get_freq_pulse_frequency()

    def meter_resist_enable(self, enable):
        self.amp.meter_resist_enable(enable)
        pass

    def get_meter_resist_enable(self):
        return self.amp.get_meter_resist_enable()

    def set_leak_comp_enable(self, enable):
        self.amp.set_leak_comp_enable(enable)
        pass

    def get_leak_res(self):
        return self.amp.get_leak_res()

    def auto_leak_res(self):
        self.amp.auto_leak_res()
        pass

    def set_primary_signal_membcur(self):
        self.amp.set_primary_signal_membcur()
        pass

    def get_primary_signal_membcur(self):
        return self.amp.get_primary_signal_membcur()

    def set_primary_signal_gain(self, gain):
        self.amp.set_primary_signal_gain(gain)
        pass

    def set_primary_signal_lpf(self, lpf):
        self.amp.set_primary_signal_lpf(lpf)
        pass

    def set_primary_signal_hpf(self, hpf):
        self.amp.set_primary_signal_hpf(hpf)
        pass

    def set_secondary_signal_membpot(self):
        self.amp.set_secondary_signal_membpot()
        pass

    def get_secondary_signal_membpot(self):
        self.amp.get_secondary_signal_membpot()
        pass

    def set_secondary_signal_lpf(self, lpf):
        self.amp.set_secondary_signal_lpf(lpf)
        pass

    def set_secondary_signal_gain(self, gain):
        self.amp.set_secondary_signal_gain(gain)
        pass

    def auto_pipette_offset(self):
        self.amp.auto_pipette_offset()
        pass

    def get_meter_value(self):
        return self.amp.get_meter_value()

    def set_holding_enable(self, enable):
        self.amp.set_holding_enable(enable)
        pass

    def set_holding(self, value):
        self.amp.set_holding(value)
        pass

    def close(self):
        self.amp.close()
        pass


if __name__ == '__main__':
    import time
    from matplotlib.pyplot import *

    val = []
    print('Connecting to the MultiClamp amplifier')
    mcc = FakeMultiClamp()
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
