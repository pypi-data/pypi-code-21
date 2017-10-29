#!/usr/bin/env python
"""This is the top-level package for various other general purpose packages. It
exists in order keep the other packages tidily hidden within a single name
space. The sub-packages available are:

`App`
    Tools to help with writing applications

`Extras`
    Third party code files used by CleverSheep.

`Log`
    Useful things for logging support.

`Prog`
    Provides various general programming tools.

`Sys`
    Platform Selection Support

`Test`
    Provides general support for testing.

`TextTools`
    Text manipulation tools

`TTY_Utils`
    Provides utilities associated with logging to terminals and related
    activities.

`VisTools`
    Tools to help visualisation. Most notably, at the moment,
    the sequence chart drawing module.


The "Clever Sheep" was called Harold.
"""


# Try to import the version string but don't fail if we can't
try:
    from version import version_string
except:
    pass
