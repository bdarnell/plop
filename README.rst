Plop: Python Low-Overhead Profiler
==================================

Plop is a stack-sampling profiler for Python.  Profile collection can be
turned on and off in a live process with minimal performance impact.

Plop is currently a work in progress and pretty rough around the edges,
so be prepared to run into bugs and extremely unrefined interfaces
(which are likely to change in backwards-incompatible ways in future
releases).

Installation
------------

::

    pip install plop

Prerequisites
-------------

The ``plop.collector`` module runs on Python 2.5, 2.6, and 2.7 on Unixy
platforms including Linux, BSD and Mac OS X (must support the ``setitimer``
system call).  The ``plop.viewer`` module requires Python 2.7 and Tornado
2.x.  The viewer can be (and usually is) run separately from the collector.

Usage
-----

In the application to be profiled, create a ``plop.collector.Collector``,
call ``start()``, wait, then ``stop()``.  Dump ``collector.stack_counts``
to a file.  See ``ProfileHandler`` in ``demo/busy_server.py`` for an example
of how to trigger profiling via an HTTP interface.

To use the viewer, run::

    python -m plop.viewer --datadir=demo/profiles

and go to http://localhost:8888

Example
-------

An end-to-end demo is available in the ``demo`` directory.
``create_profile.sh`` will run a server (which talks to itself to
generate load), generate a profile, and shut it down.  ``view_profile.sh``
will run the viewer app.

More info
---------

The source code is hosted at https://github.com/bdarnell/plop
