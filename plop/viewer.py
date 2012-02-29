#!/usr/bin/env python

import os

from tornado.ioloop import IOLoop
from tornado.options import define, options, parse_command_line
from tornado.web import RequestHandler, Application

from plop.pstats_loader import load_pstats

define('port', default=8888)
define('debug', default=False)
define('address', default='')
define('data', default=os.path.join(os.path.dirname(__file__), 'test/testdata/tornado_tests.pstats'))

class IndexHandler(RequestHandler):
    def get(self):
        self.render('index.html')

class ViewHandler(RequestHandler):
    def get(self, view):
        self.render('%s.html' % view)

class DataHandler(RequestHandler):
    def initialize(self, graph):
        self.graph = graph
    
    def get(self):
        MAX_NODES = 200
        nodes=[dict(attrs=node.attrs, weights=node.weights, id=node.id)
               for node in self.graph.nodes.itervalues()
               if 'tornado' in node.attrs['fullpath']]
        nodes = sorted(nodes, key=lambda n: -n['weights']['calls'])[:MAX_NODES]
        index = {node['id']: i for i, node in enumerate(nodes)}
        edges = [dict(source=index[edge.parent.id],
                      target=index[edge.child.id],
                      weights=edge.weights)
                 for edge in self.graph.edges.itervalues() if edge.parent.id in index and edge.child.id in index]
        self.write(dict(nodes=nodes, edges=edges))

def main():
    parse_command_line()

    graph = load_pstats(options.data)

    handlers = [
        ('/', IndexHandler),
        ('/(treemap|force|circles)', ViewHandler),
        ('/data', DataHandler, dict(graph=graph)),
        ]

    settings=dict(
        debug=options.debug,
        static_path=os.path.join(os.path.dirname(__file__), 'static'),
        template_path=os.path.join(os.path.dirname(__file__), 'templates'),
        )

    app = Application(handlers, **settings)
    app.listen(options.port, address=options.address)
    IOLoop.instance().start()
    
if __name__ == '__main__':
    main()
