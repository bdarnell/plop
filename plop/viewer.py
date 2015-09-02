#!/usr/bin/env python

from collections import Counter
import logging
import os

from tornado.ioloop import IOLoop
from tornado.options import define, options, parse_command_line
from tornado.web import RequestHandler, Application
import six

from plop.callgraph import CallGraph

define('port', default=8888)
define('debug', default=False)
define('address', default='')
define('datadir', default='profiles')

class IndexHandler(RequestHandler):
    def get(self):
        files = []
        for filename in os.listdir(options.datadir):
            mtime = os.stat(os.path.join(options.datadir, filename)).st_mtime
            files.append((mtime, filename))
        # sort by descending mtime then ascending filename
        files.sort(key=lambda x: (-x[0], x[1]))
        self.render('index.html', files=[f[1] for f in files])

class ViewHandler(RequestHandler):
    def get(self):
        self.render('force.html', filename=self.get_argument("filename"))

class ViewFlatHandler(RequestHandler):
    def get(self):
        self.render('force-flat.html',
                    data=profile_to_json(self.get_argument('filename')))

    def embed_file(self, filename):
        with open(os.path.join(self.settings['static_path'], filename)) as f:
            return f.read()

class DataHandler(RequestHandler):
    def get(self):
        self.write(profile_to_json(self.get_argument('filename')))

def profile_to_json(filename):
    root = os.path.abspath(options.datadir) + os.path.sep
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
    #index = {node['id']: i for i, node in enumerate(nodes)}
    index = dict([(node['id'], i) for i, node in enumerate(nodes)])


    # High-degree nodes are generally common utility functions, and
    # creating edges from all over the graph tends to obscure more than
    # it helps.
    degrees = Counter()
    dropped = set()
    for edge in six.itervalues(graph.edges):
        degrees[edge.child.id] += 1
        degrees[edge.parent.id] += 1
    for node, degree in six.iteritems(degrees):
        if degree > 6:
            dropped.add(node)

    edges = [dict(source=index[edge.parent.id],
                  target=index[edge.child.id],
                  weights=edge.weights)
             for edge in six.itervalues(graph.edges)
             if (edge.parent.id in index and
                 edge.child.id in index and
                 edge.parent.id not in dropped and
                 edge.child.id not in dropped)]
    stacks = [dict(nodes=[index[n.id] for n in stack.nodes],
                   weights=stack.weights)
              for stack in top_stacks]
    return dict(nodes=nodes, edges=edges, stacks=stacks)

def main():
    parse_command_line()

    handlers = [
        ('/', IndexHandler),
        ('/view', ViewHandler),
        ('/view-flat', ViewFlatHandler),
        ('/data', DataHandler),
        ]

    settings=dict(
        debug=options.debug,
        static_path=os.path.join(os.path.dirname(__file__), 'static'),
        template_path=os.path.join(os.path.dirname(__file__), 'templates'),
        )

    app = Application(handlers, **settings)
    app.listen(options.port, address=options.address)
    print("server starting at http://%s:%s" % (options.address or 'localhost',
                                               options.port))
    IOLoop.instance().start()

if __name__ == '__main__':
    main()
