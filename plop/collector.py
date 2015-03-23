from __future__ import with_statement
import collections
import os
import signal
import sys
import thread
import time
import argparse
from plop import platform


class Collector(object):
    MODES = {
        'prof': (platform.ITIMER_PROF, signal.SIGPROF),
        'virtual': (platform.ITIMER_VIRTUAL, signal.SIGVTALRM),
        'real': (platform.ITIMER_REAL, signal.SIGALRM),
    }

    def __init__(self, interval=0.01, mode='virtual', flamegraph=False):
        self.interval = interval
        self.mode = mode
        self.flamegraph = flamegraph
        assert mode in Collector.MODES
        timer, sig = Collector.MODES[self.mode]
        signal.signal(sig, self.handler)
        signal.siginterrupt(sig, False)
        self.reset()

    def reset(self):
        # defaultdict instead of counter for pre-2.7 compatibility
        self.stack_counts = collections.defaultdict(int)
        self.stacks = list()
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
            pass  # need busy wait; ITIMER_PROF doesn't proceed while sleeping

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
            if self.flamegraph:
                self.stacks.append(frames)
            else:
                self.stack_counts[tuple(frames)] += 1
        end = time.time()
        self.samples_taken += 1
        self.sample_time += (end - start)

    def filter(self, max_stacks):
        self.stack_counts = dict(sorted(self.stack_counts.iteritems(), key=lambda kv: -kv[1])[:max_stacks])


def main():
    # TODO: more options, refactor this into somewhere shared
    # between tornado.autoreload and auto2to3
    parser = argparse.ArgumentParser(description="Plop: Python Low-Overhead Profiler",
                                     prog="python -m plop.collector")
    parser.add_argument("--flamegraph", "-f", help="Record stack traces in Flamegraph format",
                        action="store_const", const=True, default=False)
    parser.add_argument("--module", "-m", help="Execute target as a module",
                        action="store_const", const=True, default=False)
    parser.add_argument("--mode", help=("Interval timer mode to use, see `man 2 setitimer`. "
                        "Default: prof"), choices=["prof", "real", "virtual"], default="prof")
    parser.add_argument("--interval", help="Timer interval in seconds. Default: 0.01",
                        default=0.01, type=float)
    parser.add_argument("--duration", help="profiling duration in seconds. Default: 3600",
                        default=3600, type=int)
    parser.add_argument("target", help="Module or script to run")
    parser.add_argument("arguments", nargs=argparse.REMAINDER,
                        help="Pass-through arguments for the profiled application")
    args = parser.parse_args()
    sys.argv = [args.target] + args.arguments

    if not os.path.exists('profiles'):
        os.mkdir('profiles')
    filename = 'profiles/%s-%s.plop' % (args.target,
                                        time.strftime('%Y%m%d-%H%M-%S'))

    collector = Collector(flamegraph=args.flamegraph, mode=args.mode, interval=args.interval)
    collector.start(duration=args.duration)
    exit_code = 0
    try:
        if args.module:
            import runpy
            runpy.run_module(args.target, run_name="__main__", alter_sys=True)
        else:
            with open(args.target) as f:
                global __file__
                __file__ = args.target
                # Use globals as our "locals" dictionary so that
                # something that tries to import __main__ (e.g. the unittest
                # module) will see the right things.
                exec f.read() in globals(), globals()
    except SystemExit, e:
        exit_code = e.code
    collector.stop()
    collector.filter(50)
    if collector.samples_taken:
        if args.flamegraph:
            store_flamegraph(filename, collector)
        else:
            with open(filename, 'w') as f:
                f.write(repr(dict(collector.stack_counts)))
        print "profile output saved to %s" % filename
        overhead = float(collector.sample_time) / collector.samples_taken
        print "overhead was %s per sample (%s%%)" % (
            overhead, overhead / collector.interval)
    else:
        print "no samples collected; program was too fast"
    sys.exit(exit_code)


def format_flame(stack):
    stack.reverse()
    funcs = map(lambda stack: "%s (%s:%s)" % (stack[2], stack[0], stack[1]), stack)
    return ";".join(funcs)


def store_flamegraph(filename, collector):
    with open(filename, 'w') as f:
        previous = None
        previous_count = 1
        for stack in collector.stacks:
            current = format_flame(stack)
            if current == previous:
                previous_count += 1
            else:
                f.write("%s %d\n" % (previous, previous_count))
                previous_count = 1
                previous = current
        f.write("%s %d\n" % (previous, previous_count))


if __name__ == '__main__':
    main()
