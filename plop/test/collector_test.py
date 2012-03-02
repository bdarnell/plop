import time
import unittest

from plop.collector import Collector

class CollectorTest(unittest.TestCase):
    def test_collector(self):
        start = time.time()
        collector = Collector(interval=0.01)
        collector.start()
        def a(end):
            while time.time() < end: pass
            c(time.time() + 0.1)
        def b(end):
            while time.time() < end: pass
            c(time.time() + 0.1)
        def c(end):
            while time.time() < end: pass
        a(time.time() + 0.1)
        b(time.time() + 0.2)
        c(time.time() + 0.3)
        end = time.time()
        collector.stop()
        elapsed = end - start
        self.assertTrue(0.8 < elapsed < 0.9, elapsed)

        counts = {}
        for stack, count in collector.stack_counts.iteritems():
            filtered_stack = [frame[2] for frame in stack
                              if frame[0].endswith('collector_test.py')]
            if filtered_stack:
                counts[tuple(filtered_stack)] = count
        
        expected = {
            ('a', 'test_collector'): 10,
            ('c', 'a', 'test_collector'): 10,
            ('b', 'test_collector'): 20,
            ('c', 'b', 'test_collector'): 10,
            ('c', 'test_collector'): 30,
            }
        for stack, count in expected.items():
            # every expected frame should appear in the data, but
            # the inverse is not true if the signal catches us between
            # calls.
            self.assertTrue(stack in counts)
            ratio = float(counts[stack])/float(count)
            self.assertTrue(0.70 <= ratio <= 1.25,
                            "expected %s, got %s (%s)" % 
                            (count, counts[stack], ratio))

        # cost depends on stack depth; for this tiny test I see 40-80usec
        time_per_sample = float(collector.sample_time) / collector.samples_taken
        self.assertTrue(time_per_sample < 0.000100, time_per_sample)
