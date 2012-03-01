#!/usr/bin/env python

import unittest

TEST_MODULES = [
    'plop.test.callgraph_test',
    'plop.test.collector_test',
    'plop.test.platform_test',
    'plop.test.pstats_loader_test',
    ]

def all():
    return unittest.defaultTestLoader.loadTestsFromNames(TEST_MODULES)

if __name__ == '__main__':
    import tornado.testing
    tornado.testing.main()
