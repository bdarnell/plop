from __future__ import absolute_import

from collections import namedtuple
import logging
import pstats

from plop.callgraph import CallGraph, Node

FuncSpec = namedtuple('FuncSpec', ['filename', 'lineno', 'funcname'])

# the difference between pcalls and calls has to do with recursive functions.
Timing = namedtuple('Timing', ['pcalls', 'calls', 'time', 'cumulative'])

def _make_node(func_spec):
    return Node(func_spec,
                attrs=dict(filename=func_spec.filename.rpartition('/')[-1],
                           fullpath=func_spec.filename,
                           lineno=func_spec.lineno,
                           funcname=func_spec.funcname))

def load_pstats(filename):
    graph = CallGraph()
    stats = pstats.Stats(filename)
    logging.info(`stats.stats`[:500])
    for k, v in stats.stats.iteritems():
        func_spec = FuncSpec(*k)
        timing = Timing(*v[:-1])
        callers = v[-1]
        for caller_spec, caller_timing in callers.iteritems():
            caller_spec = FuncSpec(*caller_spec)
            caller_timing = Timing(*caller_timing)
            parent = _make_node(FuncSpec(*caller_spec))
            child = _make_node(func_spec)
            graph.add_stack([parent, child], 
                            dict(time=caller_timing.time,
                                 calls=caller_timing.calls))
    return graph
