#!/usr/bin/env python

import sys
import unittest

COMMON_TESTS = [
    'plop.test.collector_test',
    'plop.test.platform_test',
    ]

VIEWER_TESTS = [
    'plop.test.callgraph_test',
    ]

# Viewer currently requires python 2.7 (for collections.Counter, could
# probably be fixed); collector supports >= 2.5.
if sys.version_info[:2] >= (2,7):
    TEST_MODULES = COMMON_TESTS + VIEWER_TESTS
else:
    TEST_MODULES = COMMON_TESTS

def all():
    return unittest.defaultTestLoader.loadTestsFromNames(TEST_MODULES)

if __name__ == '__main__':
    import tornado.testing
    tornado.testing.main()
