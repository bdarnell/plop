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

Plop runs on Python 2.7 and 3.x. The ``plop.collector`` module runs on
Unixy platforms including Linux, BSD and Mac OS X (must support the
``setitimer`` system call). The ``plop.viewer`` module requires
Tornado 2.x or newer. The viewer can be (and usually is) run
separately from the collector.

Usage
-----

In the application to be profiled, create a
``plop.collector.Collector``, call ``start()``, wait, then ``stop()``.
Create a `Formatter` (either `PlopFormatter` or `FlamegraphFormatter`)
and call its `save()` method to write the output to a file. See
``ProfileHandler`` in ``demo/busy_server.py`` for an example of how to
trigger profiling via an HTTP interface.

To profile an entire Python script, run::

    python -m plop.collector myscript.py

This will write the profile to ``./profiles/[timestamp]``. Add `-f
flamegraph` for flamegraph output.


To use the viewer for the default `.plop` output format, , run::

    python -m plop.viewer --datadir=demo/profiles

and go to http://localhost:8888. For `.flame` format, see
https://github.com/brendangregg/FlameGraph

Interpretation
--------------

In the default viewer, circle size is based on the amount of time that function was at the top of
the stack (i.e. time in that function, not any of its descendants). Arrow
thickness is based on how often that call was present anywhere in the stack.

In other words, the circle size corresponds to "time", and the arrow size
roughly corresponds to "cumulative time".

Example
-------

An end-to-end demo is available in the ``demo`` directory.
``create_profile.sh`` will run a server (which talks to itself to
generate load), generate a profile, and shut it down.  ``view_profile.sh``
will run the viewer app.

More info
---------

The source code is hosted at https://github.com/bdarnell/plop
