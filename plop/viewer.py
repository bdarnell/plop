#!/usr/bin/env python

import logging
import os

from tornado.ioloop import IOLoop
from tornado.options import define, options, parse_command_line
from tornado.web import RequestHandler, Application

from plop.callgraph import CallGraph
from plop.pstats_loader import load_pstats

define('port', default=8888)
define('debug', default=False)
define('address', default='')
define('datadir', default=os.path.join(os.path.dirname(__file__), 'test/testdata/'))

class IndexHandler(RequestHandler):
    def get(self):
        files = []
        for filename in os.listdir(options.datadir):
            mtime = os.stat(os.path.join(options.datadir, filename)).st_mtime
            files.append((mtime, filename))
        files.sort()
        self.render('index.html', files=[f[1] for f in files])

class ViewHandler(RequestHandler):
    def get(self, view):
        self.render('%s.html' % view, filename=self.get_argument("filename"))

class DataHandler(RequestHandler):
    def get(self):
        root = os.path.abspath(options.datadir) + os.path.sep
        filename = self.get_argument("filename")
        abspath = os.path.abspath(os.path.join(root, filename))
        assert (abspath + os.path.sep).startswith(root)
        graph = CallGraph.load(abspath)

        total = sum(stack.weights['calls'] for stack in graph.stacks)
        top_stacks = graph.stacks
        #top_stacks = [stack for stack in graph.stacks if stack.weights['calls'] > total*.005]
        filtered_nodes = set()
        for stack in top_stacks:
            filtered_nodes.update(stack.nodes)
        nodes=[dict(attrs=node.attrs, weights=node.weights, id=node.id)
               for node in filtered_nodes]
        nodes = sorted(nodes, key=lambda n: -n['weights']['calls'])
        index = {node['id']: i for i, node in enumerate(nodes)}
        edges = [dict(source=index[edge.parent.id],
                      target=index[edge.child.id],
                      weights=edge.weights)
                 for edge in graph.edges.itervalues()
                 if edge.parent.id in index and edge.child.id in index]
        stacks = [dict(nodes=[index[n.id] for n in stack.nodes],
                       weights=stack.weights)
                  for stack in top_stacks]
        self.write(dict(nodes=nodes, edges=edges, stacks=stacks))

def main():
    parse_command_line()

    handlers = [
        ('/', IndexHandler),
        ('/(treemap|force|circles)', ViewHandler),
        ('/data', DataHandler),
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
