from collections import Counter
import six


class Node(object):
    def __init__(self, id, attrs=None):
        self.id = id
        self.attrs = attrs or {}
        self.weights = Counter()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return 'Node(%s)' % (self.id,)

class Edge(object):
    def __init__(self, parent, child, weights):
        self.parent = parent
        self.child = child
        self.weights = Counter(weights)

    def key(self):
        return (self.parent, self.child)

    def __hash__(self):
        return hash(self.key())

    def __eq__(self, other):
        return self.key() == other.key()

    def __repr__(self):
        return 'Edge(%s, %s, %r)' % (self.parent.id, self.child.id, self.weights)

    def __iadd__(self, other):
        self.weights += other.weights
        return self

class Stack(object):
    def __init__(self, nodes, weights):
        self.nodes = nodes
        self.weights = Counter(weights)


class CallGraph(object):
    def __init__(self):
        # map Node.id: Node
        self.nodes = {}
        self.edges = {}
        self.stacks = []

    def add_stack(self, nodes, weights):
        nodes = [self.nodes.setdefault(n.id, n) for n in nodes]
        weights = Counter(weights)
        self.stacks.append(Stack(nodes, weights))
        
        for i in range(len(nodes) - 1):
            parent = nodes[i]
            child = nodes[i + 1]
            edge = Edge(parent, child, weights)
            if edge.key() in self.edges:
                self.edges[edge.key()] += edge
            else:
                self.edges[edge.key()] = edge
        nodes[-1].weights += weights

    def get_top_edges(self, weight, num=10):
        # TODO: is there a partial sort in python?
        sorted_edges = sorted(six.itervalues(self.edges),
                              key=lambda e: e.weights.get(weight, 0),
                              reverse=True)
        return sorted_edges[:num]

    def get_top_nodes(self, weight, num=10):
        sorted_nodes = sorted(six.itervalues(self.nodes),
                              key=lambda n: n.weights.get(weight, 0),
                              reverse=True)
        return sorted_nodes[:num]

    @staticmethod
    def load(filename):
        import ast
        with open(filename) as f:
            data = ast.literal_eval(f.read())
        graph = CallGraph()
        for stack, count in six.iteritems(data):
            stack_nodes = [Node(id=frame, attrs=dict(fullpath=frame[0],
                                                     filename=frame[0].rpartition('/')[-1],
                                                     lineno=frame[1],
                                                     funcname=frame[2]))
                           for frame in reversed(stack)]
            # TODO: this shouldn't be recorded as "calls"
            graph.add_stack(stack_nodes, weights=dict(calls=count))
        return graph

if __name__ == '__main__':
    import sys
    graph = CallGraph.load(sys.argv[1])
