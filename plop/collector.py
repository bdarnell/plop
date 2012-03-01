import collections
import signal
import time
from plop import platform

class Collector(object):
    def __init__(self):
        # defaultdict instead of counter for pre-2.7 compatibility
        self.stack_counts = collections.defaultdict(int)
        self.samples_remaining = 0
        self.stopping = False
        self.stopped = False

        self.samples_taken = 0
        self.sample_time = 0

    def start(self, interval=0.01, duration=30.0):
        self.stopping = False
        self.stopped = False
        self.samples_remaining = int(duration / interval)
        signal.signal(signal.SIGPROF, self.handler)
        platform.setitimer(platform.ITIMER_PROF, interval, interval)

    def stop(self):
        self.stopping = True
        self.wait()

    def wait(self):
        while not self.stopped:
            pass # need busy wait; ITIMER_PROF doesn't proceed while sleeping

    def handler(self, sig, frame):
        start = time.time()
        self.samples_remaining -= 1
        if self.samples_remaining <= 0 or self.stopping:
            platform.setitimer(platform.ITIMER_PROF, 0, 0)
            self.stopped = True
            return
        frames = []
        while frame is not None:
            code = frame.f_code
            frames.append((code.co_filename, code.co_firstlineno, code.co_name))
            frame = frame.f_back
        self.stack_counts[tuple(frames)] += 1
        end = time.time()
        self.samples_taken += 1
        self.sample_time += (end - start)

