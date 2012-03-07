from __future__ import with_statement
import collections
import signal
import sys
import thread
import time
from plop import platform

class Collector(object):
    MODES = {
        'prof': (platform.ITIMER_PROF, signal.SIGPROF),
        'virtual': (platform.ITIMER_VIRTUAL, signal.SIGVTALRM),
        'real': (platform.ITIMER_REAL, signal.SIGALRM),
        }

    def __init__(self, interval=0.01, mode='virtual'):
        self.interval = interval
        self.mode = mode
        assert mode in Collector.MODES
        timer, sig = Collector.MODES[self.mode]
        signal.signal(sig, self.handler)
        self.reset()

    def reset(self):
        # defaultdict instead of counter for pre-2.7 compatibility
        self.stack_counts = collections.defaultdict(int)
        self.samples_remaining = 0
        self.stopping = False
        self.stopped = False

        self.samples_taken = 0
        self.sample_time = 0

    def start(self, duration=30.0):
        self.stopping = False
        self.stopped = False
        self.samples_remaining = int(duration / self.interval)
        timer, sig = Collector.MODES[self.mode]
        platform.setitimer(timer, self.interval, self.interval)

    def stop(self):
        self.stopping = True
        self.wait()

    def wait(self):
        while not self.stopped:
            pass # need busy wait; ITIMER_PROF doesn't proceed while sleeping

    def handler(self, sig, current_frame):
        start = time.time()
        self.samples_remaining -= 1
        if self.samples_remaining <= 0 or self.stopping:
            platform.setitimer(Collector.MODES[self.mode][0], 0, 0)
            self.stopped = True
            return
        current_tid = thread.get_ident()
        for tid, frame in sys._current_frames().items():
            if tid == current_tid:
                frame = current_frame
            frames = []
            while frame is not None:
                code = frame.f_code
                frames.append((code.co_filename, code.co_firstlineno, code.co_name))
                frame = frame.f_back
            self.stack_counts[tuple(frames)] += 1
        end = time.time()
        self.samples_taken += 1
        self.sample_time += (end - start)

    def filter(self, max_stacks):
        self.stack_counts = dict(sorted(self.stack_counts.iteritems(), key=lambda kv: -kv[1])[:max_stacks])


def main():
    # TODO: more options, refactor this into somewhere shared
    # between tornado.autoreload and auto2to3
    if len(sys.argv) >= 3 and sys.argv[1] == '-m':
        mode = 'module'
        module = sys.argv[2]
        del sys.argv[1:3]
    elif len(sys.argv) >= 2:
        mode = "script"
        script = sys.argv[1]
        sys.argv = sys.argv[1:]
    else:
        print "usage: python -m plop.collector -m module_to_run"
        sys.exit(1)
    

    collector = Collector()
    collector.start(duration=3600)
    exit_code = 0
    try:
        if mode == "module":
            import runpy
            runpy.run_module(module, run_name="__main__", alter_sys=True)
        elif mode == "script":
            with open(script) as f:
                global __file__
                __file__ = script
                # Use globals as our "locals" dictionary so that
                # something that tries to import __main__ (e.g. the unittest
                # module) will see the right things.
                exec f.read() in globals(), globals()
    except SystemExit, e:
        exit_code = e.code
    collector.stop()
    collector.filter(50)
    with open('/tmp/plop.out', 'w') as f:
        f.write(repr(dict(collector.stack_counts)))
    print "profile output saved to /tmp/plop.out"
    overhead = float(collector.sample_time) / collector.samples_taken
    print "overhead was %s per sample (%s%%)" % (
        overhead, overhead / collector.interval)
    sys.exit(exit_code)

if __name__ == '__main__':
    main()

