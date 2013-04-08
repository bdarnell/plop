import time
import os
import functools
from plop.collector import Collector


def plop(log_to="/tmp/plop", log_file=None):
    """ Decorator for your functions. Use this to profile your slow functions
        by adding a @plop(). 
        
        @plop()
        def slow_function():
            return slow_stuff

    """
    if log_file is None:
        log_file = str(int(time.time())) + ".log"

    def decorator(function):
        @functools.wraps(function)

        def wrapper(*args, **kwargs):
            log = os.path.join(log_to,log_file)
            plop = Collector()
            plop.start()
            result = function(*args, **kwargs)
            plop.stop()
            with open(log, 'a') as f:
                f.write(repr(dict(plop.stack_counts)))
            return result

        return wrapper
    return decorator
