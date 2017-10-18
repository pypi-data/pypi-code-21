# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see spyder/__init__.py for details)

"""Module checking Spyder runtime dependencies"""


import os

# Local imports
from spyder.utils import programs


class Dependency(object):
    """Spyder's dependency

    version may starts with =, >=, > or < to specify the exact requirement ;
    multiple conditions may be separated by ';' (e.g. '>=0.13;<1.0')"""

    OK = 'OK'
    NOK = 'NOK'

    def __init__(self, modname, features, required_version,
                 installed_version=None, optional=False):
        self.modname = modname
        self.features = features
        self.required_version = required_version
        self.optional = optional
        if installed_version is None:
            try:
                self.installed_version = programs.get_module_version(modname)
            except:
                # NOTE: Don't add any exception type here!
                # Modules can fail to import in several ways besides
                # ImportError
                self.installed_version = None
        else:
            self.installed_version = installed_version

    def check(self):
        """Check if dependency is installed"""
        return programs.is_module_installed(self.modname,
                                            self.required_version,
                                            self.installed_version)

    def get_installed_version(self):
        """Return dependency status (string)"""
        if self.check():
            return '%s (%s)' % (self.installed_version, self.OK)
        else:
            return '%s (%s)' % (self.installed_version, self.NOK)
    
    def get_status(self):
        """Return dependency status (string)"""
        if self.check():
            return self.OK
        else:
            return self.NOK


DEPENDENCIES = []


def add(modname, features, required_version, installed_version=None,
        optional=False):
    """Add Spyder dependency"""
    global DEPENDENCIES
    for dependency in DEPENDENCIES:
        if dependency.modname == modname:
            raise ValueError("Dependency has already been registered: %s"\
                             % modname)
    DEPENDENCIES += [Dependency(modname, features, required_version,
                                installed_version, optional)]


def check(modname):
    """Check if required dependency is installed"""
    for dependency in DEPENDENCIES:
        if dependency.modname == modname:
            return dependency.check()
    else:
        raise RuntimeError("Unkwown dependency %s" % modname)


def status(deps=DEPENDENCIES, linesep=os.linesep):
    """Return a status of dependencies"""
    maxwidth = 0
    col1 = []
    col2 = []
    for dependency in deps:
        title1 = dependency.modname
        title1 += ' ' + dependency.required_version
        col1.append(title1)
        maxwidth = max([maxwidth, len(title1)])
        col2.append(dependency.get_installed_version())
    text = ""
    for index in range(len(deps)):
        text += col1[index].ljust(maxwidth) + ':  ' + col2[index] + linesep
    return text


def missing_dependencies():
    """Return the status of missing dependencies (if any)"""
    missing_deps = []
    for dependency in DEPENDENCIES:
        if not dependency.check() and not dependency.optional:
            missing_deps.append(dependency)
    if missing_deps:
        return status(deps=missing_deps, linesep='<br>')
    else:
        return ""
