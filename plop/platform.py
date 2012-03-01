import signal

if hasattr(signal, 'setitimer'):
    from signal import setitimer, ITIMER_REAL, ITIMER_VIRTUAL, ITIMER_PROF
else:
    # python2.5 doesn't have setitimer
    import ctypes.util
    libc = ctypes.CDLL(ctypes.util.find_library("c"))
    class Timeval(ctypes.Structure):
        _fields_ = [('tv_sec', ctypes.c_long), ('tv_usec', ctypes.c_long)]
    class Itimerval(ctypes.Structure):
        _fields_ = [('it_interval', Timeval), ('it_value', Timeval)]
    libc.setitimer.argtypes = [ctypes.c_int, ctypes.POINTER(Itimerval),
                               ctypes.POINTER(Itimerval)]
    def seconds_to_timeval(seconds):
        return Timeval(int(seconds), int((seconds % 1) * 1000000))
    def setitimer(which, seconds, interval):
        libc.setitimer(which, 
                       Itimerval(seconds_to_timeval(interval),
                                 seconds_to_timeval(seconds)),
                       # We should get the output value here to return,
                       # but we don't need it right now.
                       None)
    ITIMER_REAL = 0
    ITIMER_VIRTUAL = 1
    ITIMER_PROF = 2
