import logging
import os
import pprint
from tornado.testing import LogTrapTestCase

from plop.pstats import load_pstats

class TornadoPstatsTest(LogTrapTestCase):
    def setUp(self):
        # parsing this file currently takes ~0.5s
        self.graph = load_pstats(os.path.join(os.path.dirname(__file__),
                                              'testdata/tornado_tests.pstats'))

    def format_node(self, node):
        return '%s:%d:%s' % (node.attrs['filename'], node.attrs['lineno'],
                             node.attrs['funcname'])

    def format_value(self, value):
        if value == int(value):
            return str(value)
        else:
            return '%.3f' % value

    def summarize_node(self, node, weight):
        return (self.format_node(node), self.format_value(node.weights[weight]))

    def summarize_edge(self, edge, weight):
        return (self.format_node(edge.parent), self.format_node(edge.child),
                self.format_value(edge.weights[weight]))

    def test_top_nodes(self):
        nodes = self.graph.get_top_nodes('time', num=5)
        self.assertEqual(
            [self.summarize_node(n, 'time') for n in nodes],
            [("~:0:<method 'control' of 'select.kqueue' objects>", "0.125"),
             ('~:0:<posix.fork>', "0.044"),
             ('~:0:<built-in method do_handshake>', "0.044"),
             ('~:0:<_socket.getaddrinfo>', "0.044"),
             ('~:0:<posix.wait>', "0.042"),
             ])

        nodes = self.graph.get_top_nodes('calls', num=5)
        self.assertEqual(
            [self.summarize_node(n, 'calls') for n in nodes],
            [('~:0:<len>', '30221'),
             ("~:0:<method 'append' of 'list' objects>", '20400'),
             ('~:0:<isinstance>', '15689'),
             ('~:0:<getattr>', '10198'),
             ("~:0:<method 'startswith' of 'str' objects>", '8273'),
             ])

        edges = self.graph.get_top_edges('calls', num=5)
        self.assertEqual(
            [self.summarize_edge(e, 'calls') for e in edges],
            [('sre_parse.py:182:__next', '~:0:<len>', '10327'),
             ('loader.py:134:isTestMethod',
              "~:0:<method 'startswith' of 'str' objects>",
              '6979'),
             ('~:0:<filter>', 'loader.py:134:isTestMethod', '6979'),
             ('sre_compile.py:32:_compile',
              "~:0:<method 'append' of 'list' objects>",
              '5458'),
             ('sre_parse.py:201:get', 'sre_parse.py:182:__next', '4663'),
             ])
