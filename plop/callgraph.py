from collections import Counter


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



class CallGraph(object):
    def __init__(self):
        # map Node.id: Node
        self.nodes = {}
        self.edges = {}

    def add_stack(self, nodes, weights):
        assert len(nodes) > 1
        nodes = [self.nodes.setdefault(n.id, n) for n in nodes]
        weights = Counter(weights)
        
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
        sorted_edges = sorted(self.edges.values(),
                              key=lambda e: e.weights.get(weight, 0),
                              reverse=True)
        return sorted_edges[:num]

    def get_top_nodes(self, weight, num=10):
        sorted_nodes = sorted(self.nodes.values(),
                              key=lambda n: n.weights.get(weight, 0),
                              reverse=True)
        return sorted_nodes[:num]
