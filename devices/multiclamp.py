'''
Basic Interface to the MultiClamp 700A and 700B amplifiers. 
'''
import ctypes
import os
import logging
import time

NO_ERROR = 6000
logger = logging.Logger(__name__)


class MultiClamp(object):
    def __init__(self, dll_path=r'C:\Program Files\Molecular Devices\MultiClamp 700B Commander\3rd Party Support\AxMultiClampMsg'):
        self.dll = ctypes.WinDLL(os.path.join(dll_path, 'AxMultiClampMsg.dll'))
        self.last_error = ctypes.c_int(NO_ERROR)
        self.error_msg = ctypes.create_string_buffer(256)
        self.msg_handler = self.dll.MCCMSG_CreateObject(ctypes.byref(self.last_error))
        self.check_error(fail=True)
        # TODO: Only supports one channel (i.e. headstage) for now
        self.find_and_select_amplifier()

    def check_error(self, fail=False):
        if self.last_error != NO_ERROR:
            # Get the error text
            self.dll.CLXMSG_BuildErrorText(self.msg_handler,
                                           self.last_error,
                                           self.error_msg,
                                           ctypes.c_uint(256))
            full_error = ('An error occurred while communicating with the '
                          'MultiClamp amplifier: {}'.format(self.error_msg))
            if fail:
                raise IOError(full_error)
            else:
                logger.warn(full_error)
            # Reset the error code
            self.last_error.value = NO_ERROR

    def find_and_select_amplifier(self):
        model = ctypes.c_uint()
        port = ctypes.c_uint()
        device = ctypes.c_uint()
        channel = ctypes.c_uint()
        serial = ctypes.create_string_buffer(16)
        if not self.dll.MCCMSG_FindFirstMultiClamp(self.msg_handler,
                                                   ctypes.byref(model),
                                                   serial,
                                                   ctypes.c_uint(16),  # buffer size
                                                   ctypes.byref(port),
                                                   ctypes.byref(device),
                                                   ctypes.byref(channel),
                                                   ctypes.byref(self.last_error)):
            self.check_error(fail=True)
        if model.value == 0:  # 700A
            logger.info(('Found a MultiClamp 700A (Port: {}, Device: {}, '
                         'Channel: {})').format(port.value, device.value,
                                                channel.value))
        elif model.value == 1:  # 700B
            logger.info(('Found a MultiClamp 700B (Serial number: {}, '
                         'Channel: {})').format(serial.value, channel.value))
        else:
            raise AssertionError('Unknown model')

        if not self.dll.MCCMSG_SelectMultiClamp(self.msg_handler,
                                                model,
                                                serial,
                                                port,
                                                device,
                                                channel,
                                                ctypes.byref(self.last_error)):
            self.check_error(fail=True)

    def voltage_clamp(self):
        # MCCMSG_MODE_VCLAMP = 0
        if not self.dll.MCCMSG_SetMode(self.msg_handler, ctypes.c_uint(0),
                                       ctypes.byref(self.last_error)):
            self.check_error()

    def current_clamp(self):
        # MCCMSG_MODE_ICLAMP = 1
        if not self.dll.MCCMSG_SetMode(self.msg_handler, ctypes.c_uint(1),
                                       ctypes.byref(self.last_error)):
            self.check_error()

    def get_fast_compensation_capacitance(self):
        capacitance = ctypes.c_double(0.)
        if not self.dll.MCCMSG_GetFastCompCap(self.msg_handler,
                                              ctypes.byref(capacitance),
                                              ctypes.byref(self.last_error)):
            self.check_error()
        return capacitance

    def set_fast_compensation_capacitance(self, capacitance):
        if not self.dll.MCCMSG_SetFastCompCap(self.msg_handler,
                                              ctypes.c_double(capacitance),
                                              ctypes.byref(self.last_error)):
            self.check_error()

    def auto_fast_compensation(self):
        if not self.dll.MCCMSG_AutoFastComp(self.msg_handler,
                                            ctypes.byref(self.last_error)):
            self.check_error()

    def get_slow_compensation_capacitance(self):
        capacitance = ctypes.c_double(0.)
        if not self.dll.MCCMSG_GetSlowCompCap(self.msg_handler,
                                              ctypes.byref(capacitance),
                                              ctypes.byref(self.last_error)):
            self.check_error()
        return capacitance

    def set_slow_compensation_capacitance(self, capacitance):
        if not self.dll.MCCMSG_SetSlowCompCap(self.msg_handler,
                                              ctypes.c_double(capacitance),
                                              ctypes.byref(self.last_error)):
            self.check_error()

    def auto_slow_compensation(self):
        if not self.dll.MCCMSG_AutoSlowComp(self.msg_handler,
                                            ctypes.byref(self.last_error)):
            self.check_error()


    def close(self):
        self.dll.MCCMSG_DestroyObject(self.msg_handler)
        self.msg_handler = None


if __name__ == '__main__':
    print('Connecting to the MultiClamp amplifier')
    mcc = MultiClamp()
    print('Switching to current clamp')
    mcc.current_clamp()
    time.sleep(2)
    print('Switching to voltage clamp')
    mcc.voltage_clamp()
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
