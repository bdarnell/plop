import signal
import time
import unittest

from plop import platform

class WorkaroundTests(unittest.TestCase):
    def test_seconds_to_timeval(self):
        def tup(tv): return (tv.tv_sec, tv.tv_usec)
        self.assertEqual(tup(platform.seconds_to_timeval(1)), (1, 0))
        self.assertEqual(tup(platform.seconds_to_timeval(2.5)), (2, 500000))
        # We lose a little precision at the low end.  Oh well, we're probably
        # not getting microsecond accuracy in python anyway.
        self.assertEqual(tup(platform.seconds_to_timeval(1.000010)), (1, 10))

if hasattr(signal, 'setitimer'):
    del WorkaroundTests

class ItimerTests(unittest.TestCase):
    def test_timer(self):
        result = []
        def handler(sig, frame):
            result.append(None)  # peano arithmetic ftw
        signal.signal(signal.SIGPROF, handler)
        platform.setitimer(platform.ITIMER_PROF, 0.01, 0.01)
        start = time.time()
        # must busy-wait because if we're sleeping python signal handlers
        # don't run.
        while time.time() < start + 0.5: pass
        platform.setitimer(platform.ITIMER_PROF, 0, 0)
        end = time.time()
        elapsed = end - start
        self.assertTrue(0.500 < elapsed < 0.501, elapsed)
        count = len(result)
        # We should have gotten ~50 timer ticks while we waited.
        # in practice I see ~44 on my mac, and ~48 on a linux
        # vm running on that same mac (?!)
        self.assertTrue(37 < count < 55, count)
