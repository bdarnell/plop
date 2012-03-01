from collections import defaultdict
import time
import unittest

from plop.collector import Collector

class CollectorTest(unittest.TestCase):
    def test_collector(self):
        start = time.time()
        collector = Collector()
        collector.start(interval=0.01)
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

        filtered_stacks = []
        for stack in collector.stacks:
            filtered_stack = [frame[2] for frame in stack 
                              if frame[0].endswith('collector_test.py')]
            if filtered_stack:
                filtered_stacks.append(tuple(filtered_stack))

        counts = defaultdict(int)
        for stack in filtered_stacks:
            counts[stack] += 1
        
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
