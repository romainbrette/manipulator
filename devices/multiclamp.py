'''
Basic Interface to the MultiClamp 700A and 700B amplifiers. 
'''
import ctypes
import functools
import os
import logging
import time

NO_ERROR = 6000

def needs_select(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwds):
        if not MultiClamp.selected_device == self:
            self.select_amplifier()
        func(self, *args, **kwds)
    return wrapper

def _identify_amplifier(model, serial, port, device, channel):
    if model.value == 0:  # 700A
        logging.info(('Found a MultiClamp 700A (Port: {}, Device: {}, '
                      'Channel: {})').format(port.value, device.value,
                                             channel.value))
        return {'model': '700A', 'port': port.value, 'device': device.value,
                'channel': channel.value}
    elif model.value == 1:  # 700B
        logging.info(('Found a MultiClamp 700B (Serial number: {}, '
                      'Channel: {})').format(serial.value, channel.value))
        return {'model': '700B', 'serial': serial.value,
                'channel': channel.value}
    else:
        raise AssertionError('Unknown model')


class MultiClamp(object):
    dll_path = r'C:\Program Files\Molecular Devices\MultiClamp 700B Commander\3rd Party Support\AxMultiClampMsg'
    all_devices = None
    selected_device = None

    def __init__(self, **kwds):
        self.dll = ctypes.WinDLL(os.path.join(MultiClamp.dll_path,
                                              'AxMultiClampMsg.dll'))
        self.last_error = ctypes.c_int(NO_ERROR)
        self.error_msg = ctypes.create_string_buffer(256)
        self.msg_handler = self.dll.MCCMSG_CreateObject(ctypes.byref(self.last_error))
        self.check_error(fail=True)
        if MultiClamp.all_devices is None:
            MultiClamp.all_devices = self.find_amplifiers()
        print MultiClamp.all_devices
        self.identification = kwds
        self.select_amplifier()
        MultiClamp.selected_device = self

    def check_error(self, fail=False):
        if self.last_error.value != NO_ERROR:
            # Get the error text
            self.dll.MCCMSG_BuildErrorText(self.msg_handler,
                                           self.last_error,
                                           self.error_msg,
                                           ctypes.c_uint(256))
            full_error = ('An error occurred while communicating with the '
                          'MultiClamp amplifier: {}'.format(self.error_msg.value))
            if fail:
                raise IOError(full_error)
            else:
                logging.warn(full_error)
            # Reset the error code
            self.last_error.value = NO_ERROR

    def find_amplifiers(self):
        model = ctypes.c_uint()
        port = ctypes.c_uint()
        device = ctypes.c_uint()
        channel = ctypes.c_uint()
        serial = ctypes.create_string_buffer(16)
        devices = []
        if self.dll.MCCMSG_FindFirstMultiClamp(self.msg_handler,
                                               ctypes.byref(model),
                                               serial,
                                               ctypes.c_uint(16),  # buffer size
                                               ctypes.byref(port),
                                               ctypes.byref(device),
                                               ctypes.byref(channel),
                                               ctypes.byref(self.last_error)):
            devices.append(_identify_amplifier(model, serial, port, device,
                                               channel))
        else:
            self.check_error()
        while self.dll.MCCMSG_FindNextMultiClamp(self.msg_handler,
                                                 ctypes.byref(model),
                                                 serial,
                                                 ctypes.c_uint(16),  # buffer size
                                                 ctypes.byref(port),
                                                 ctypes.byref(device),
                                                 ctypes.byref(channel),
                                                 ctypes.byref(self.last_error)):
            devices.append(_identify_amplifier(model, serial, port, device,
                                                   channel))
        return devices

    def select_amplifier(self):
        multiclamps = []
        for multiclamp in MultiClamp.all_devices:
            if all(multiclamp.get(key, None) == value
                   for key, value in self.identification.iteritems()):
                multiclamps.append(multiclamp)
        if len(multiclamps) == 0:
            raise RuntimeError('No device identified via {} found'.format(self.identification))
        elif len(multiclamps) > 1:
            raise RuntimeError('{} devices identified via {} found'.format(len(multiclamps),
                                                                           self.identification))
        multiclamp = multiclamps[0]
        if multiclamp['model'] == '700A':
            model = ctypes.c_uint(0)
            serial = None
            port = ctypes.c_uint(multiclamp['port'])
            device = ctypes.c_uint(multiclamp['device'])
            channel = ctypes.c_uint(multiclamp['channel'])
        elif multiclamp['model'] == '700B':
            model = ctypes.c_uint(1)
            serial = multiclamp['serial']
            port = None
            device = None
            channel = ctypes.c_uint(multiclamp['channel'])

        if not self.dll.MCCMSG_SelectMultiClamp(self.msg_handler,
                                                model,
                                                serial,
                                                port,
                                                device,
                                                channel,
                                                ctypes.byref(self.last_error)):
            self.check_error(fail=True)

    @needs_select
    def voltage_clamp(self):
        # MCCMSG_MODE_VCLAMP = 0
        if not self.dll.MCCMSG_SetMode(self.msg_handler, ctypes.c_uint(0),
                                       ctypes.byref(self.last_error)):
            self.check_error()

    @needs_select
    def current_clamp(self):
        # MCCMSG_MODE_ICLAMP = 1
        if not self.dll.MCCMSG_SetMode(self.msg_handler, ctypes.c_uint(1),
                                       ctypes.byref(self.last_error)):
            self.check_error()

    @needs_select
    def get_fast_compensation_capacitance(self):
        capacitance = ctypes.c_double(0.)
        if not self.dll.MCCMSG_GetFastCompCap(self.msg_handler,
                                              ctypes.byref(capacitance),
                                              ctypes.byref(self.last_error)):
            self.check_error()
        return capacitance

    @needs_select
    def set_fast_compensation_capacitance(self, capacitance):
        if not self.dll.MCCMSG_SetFastCompCap(self.msg_handler,
                                              ctypes.c_double(capacitance),
                                              ctypes.byref(self.last_error)):
            self.check_error()

    @needs_select
    def auto_fast_compensation(self):
        if not self.dll.MCCMSG_AutoFastComp(self.msg_handler,
                                            ctypes.byref(self.last_error)):
            self.check_error()

    @needs_select
    def get_slow_compensation_capacitance(self):
        capacitance = ctypes.c_double(0.)
        if not self.dll.MCCMSG_GetSlowCompCap(self.msg_handler,
                                              ctypes.byref(capacitance),
                                              ctypes.byref(self.last_error)):
            self.check_error()
        return capacitance

    @needs_select
    def set_slow_compensation_capacitance(self, capacitance):
        if not self.dll.MCCMSG_SetSlowCompCap(self.msg_handler,
                                              ctypes.c_double(capacitance),
                                              ctypes.byref(self.last_error)):
            self.check_error()

    @needs_select
    def auto_slow_compensation(self):
        if not self.dll.MCCMSG_AutoSlowComp(self.msg_handler,
                                            ctypes.byref(self.last_error)):
            self.check_error()


    def close(self):
        self.dll.MCCMSG_DestroyObject(self.msg_handler)
        self.msg_handler = None


if __name__ == '__main__':
    print('Connecting to the MultiClamp amplifier')
    mcc = MultiClamp(channel=1)
    print('Switching to current clamp')
    mcc.current_clamp()
    time.sleep(2)
    print('Switching to voltage clamp')
    mcc.voltage_clamp()
    print('Setting compensation values')
    mcc.set_slow_compensation_capacitance(1e-12)
    mcc.set_fast_compensation_capacitance(5e-12)
    print('Compensation values:')
    print('Slow: {}'.format(mcc.get_slow_compensation_capacitance()))
    print('Fast: {}'.format(mcc.get_fast_compensation_capacitance()))
    print('Running automatic slow compensation')
    mcc.auto_slow_compensation()
    print('Running automatic fast compensation')
    mcc.auto_fast_compensation()
    print('Compensation values:')
    print('Slow: {}'.format(mcc.get_slow_compensation_capacitance()))
    print('Fast: {}'.format(mcc.get_fast_compensation_capacitance()))
    mcc.close()
