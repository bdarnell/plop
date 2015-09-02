import ast
import logging
import threading
import time
import unittest
import six

from plop.collector import Collector, PlopFormatter

class CollectorTest(unittest.TestCase):
    def filter_stacks(self, collector):
        # Kind of hacky, but this is the simplest way to keep the tests
        # working after the internals of the collector changed to support
        # multiple formatters.
        stack_counts = ast.literal_eval(PlopFormatter().format(collector))
        counts = {}
        for stack, count in six.iteritems(stack_counts):
            filtered_stack = [frame[2] for frame in stack
                              if frame[0].endswith('collector_test.py')]
            if filtered_stack:
                counts[tuple(filtered_stack)] = count
        return counts
        
    def check_counts(self, counts, expected):
        failed = False
        output = []
        for stack, count in six.iteritems(expected):
            # every expected frame should appear in the data, but
            # the inverse is not true if the signal catches us between
            # calls.
            self.assertTrue(stack in counts)
            ratio = float(counts[stack])/float(count)
            output.append('%s: expected %s, got %s (%s)' % 
                          (stack, count, counts[stack], ratio))
            if not (0.70 <= ratio <= 1.25):
                failed = True
        if failed:
            for line in output:
                logging.warning(line)
            for key in set(counts.keys()) - set(expected.keys()):
                logging.warning('unexpected key: %s: got %s' % (key, counts[key]))
            self.fail("collected data did not meet expectations")

    def test_collector(self):
        start = time.time()
        def a(end):
            while time.time() < end: pass
            c(time.time() + 0.1)
        def b(end):
            while time.time() < end: pass
            c(time.time() + 0.1)
        def c(end):
            while time.time() < end: pass
        collector = Collector(interval=0.01, mode='prof')
        collector.start()
        a(time.time() + 0.1)
        b(time.time() + 0.2)
        c(time.time() + 0.3)
        end = time.time()
        collector.stop()
        elapsed = end - start
        self.assertTrue(0.8 < elapsed < 0.9, elapsed)

        counts = self.filter_stacks(collector)
        
        expected = {
            ('a', 'test_collector'): 10,
            ('c', 'a', 'test_collector'): 10,
            ('b', 'test_collector'): 20,
            ('c', 'b', 'test_collector'): 10,
            ('c', 'test_collector'): 30,
            }
        self.check_counts(counts, expected)

        # cost depends on stack depth; for this tiny test I see 40-80usec
        time_per_sample = float(collector.sample_time) / collector.samples_taken
        self.assertTrue(time_per_sample < 0.000100, time_per_sample)

    def test_collect_threads(self):
        start = time.time()
        def a(end):
            while time.time() < end: pass
        def thread1_func():
            a(time.time() + 0.2)
        def thread2_func():
            a(time.time() + 0.3)
        collector = Collector(interval=0.01, mode='prof')
        collector.start()
        thread1 = threading.Thread(target=thread1_func)
        thread2 = threading.Thread(target=thread2_func)
        thread1.start()
        thread2.start()
        a(time.time() + 0.1)
        while thread1.isAlive(): pass
        while thread2.isAlive(): pass
        thread1.join()
        thread2.join()
        end = time.time()
        collector.stop()
        elapsed = end - start
        self.assertTrue(0.3 < elapsed < 0.4, elapsed)

        counts = self.filter_stacks(collector)

        expected = {
            ('a', 'test_collect_threads'): 10,
            ('a', 'thread1_func'): 20,
            ('a', 'thread2_func'): 30,
            }
        self.check_counts(counts, expected)
