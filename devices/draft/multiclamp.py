import ctypes
import time


errdict = {6000: 'MCCMSG_ERROR_NOERROR', 6001: 'MCCMSG_ERROR_OUTOFMEMORY',
           6002: 'MCCMSG_ERROR_MCCNOTOPEN', 6003: 'MCCMSG_ERROR_INVALIDDLLHANDLE',
           6004: 'MCCMSG_ERROR_INVALIDPARAMETER', 6005: 'MCCMSG_ERROR_MSGTIMEOUT',
           6006: 'MCCMSG_ERROR_MCCCOMMANDFAIL'}

# global error variable
error_value = ctypes.c_int()
error_ptr = ctypes.byref(error_value)


def check_error():
    if error_value.value not in [6000, 0]:
        raise RuntimeError('An error occured: ' + errdict[error_value.value])


dll = ctypes.WinDLL('AxMultiClampMsg.dll')
error = ctypes.byref(ctypes.c_int())  # err pointer

msg_handler = dll.MCCMSG_CreateObject(error_ptr)
check_error()

model = ctypes.c_uint()
port = ctypes.c_uint()
device = ctypes.c_uint()
channel = ctypes.c_uint()
serial = ctypes.create_string_buffer(16)
if not dll.MCCMSG_FindFirstMultiClamp(msg_handler,
                                      ctypes.byref(model),
                                      serial,
                                      ctypes.c_uint(16),  # buffer size
                                      ctypes.byref(port),
                                      ctypes.byref(device),
                                      ctypes.byref(channel),
                                      error_ptr):
    check_error()

if not dll.MCCMSG_SelectMultiClamp(msg_handler,
                                   model,
                                   serial,
                                   port,
                                   device,
                                   channel,
                                   error_ptr):
    check_error()

MCCMSG_MODE_VCLAMP = ctypes.c_uint(0)
MCCMSG_MODE_ICLAMP = ctypes.c_uint(1)

# Switch to voltage clamp
print "Switching to voltage clamp"
if not dll.MCCMSG_SetMode(msg_handler, MCCMSG_MODE_VCLAMP, error_ptr):
    check_error()
time.sleep(2)

# Switch to current clamp
print "Switching to current clamp"
if not dll.MCCMSG_SetMode(msg_handler, MCCMSG_MODE_ICLAMP, error_ptr):
    check_error()

dll.MCCMSG_DestroyObject(msg_handler)
