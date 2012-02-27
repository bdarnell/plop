import logging
from tornado.testing import LogTrapTestCase

from plop.callgraph import CallGraph, Node

class SimpleCallgraphTest(LogTrapTestCase):
    def setUp(self):
        graph = CallGraph()
        graph.add_stack([Node(1), Node(2)], dict(time=1))
        graph.add_stack([Node(1), Node(3)], dict(time=3))
        graph.add_stack([Node(1), Node(2), Node(3)], dict(time=7))
        graph.add_stack([Node(1), Node(4), Node(2), Node(3)], dict(time=2))
        self.graph = graph

    def test_basic_attrs(self):
        logging.info(self.graph.nodes)
        logging.info(self.graph.edges)
        self.assertEqual(len(self.graph.nodes), 4)
        self.assertEqual(len(self.graph.edges), 5)
                
    def test_top_edges(self):
        top_edges = self.graph.get_top_edges('time', 3)
        logging.info(top_edges)
        summary = [(e.parent.id, e.child.id, e.weights['time']) for e in top_edges]
        self.assertEqual(summary, [
                (2, 3, 9),
                (1, 2, 8),
                (1, 3, 3),
                ])

    def test_top_nodes(self):
        top_nodes = self.graph.get_top_nodes('time', 2)
        logging.info(top_nodes)
        summary = [(n.id, n.weights['time']) for n in top_nodes]
        self.assertEqual(summary, [
                (3, 12),
                (2, 1),
                ])
