# -*- coding: utf-8 -*-

"""Main module."""

import semver

def compare(v1, v2):
    return semver.compare(v1, v2)

def bump(increment, version):
    increments = ['major', 'minor', 'patch', 'build', 'prerelease']
    assert(increment in increments)
    method = getattr(semver, "bump_%s" % increment)
    return method(version)

def _get_version():
    return semver.__version__
