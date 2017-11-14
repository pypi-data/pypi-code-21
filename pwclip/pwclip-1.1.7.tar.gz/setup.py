#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generic Setup script, takes package info from __pkginfo__.py file.
"""
from sys import argv
from os import listdir, chdir, getcwd, path
from setuptools import setup, find_packages

__docformat__ = "restructuredtext en"

def packages(directory):
    """return a list of subpackages for the given directory"""
    result = []
    for package in listdir(directory):
        absfile = path.join(directory, package, '__init__.py')
        if path.exists(absfile):
            result.append(path.dirname(absfile))
            result += packages(path.dirname(absfile))
    return result

def scripts(linux_scripts):
    """creates the proper script names required for each platform"""
    from distutils import util
    if util.get_platform()[:3] == 'win':
        return linux_scripts + [script + '.bat' for script in linux_scripts]
    return linux_scripts

def setupkwargs(pinf):
    """
    translate default __pkginfo__ keywords 
    to those understood by setuptools.setup
    """
    skwargs = {}
    uniss = (
        'author',
        'license',
        'version',
        'data_files',
        'description',
        'ext_modules',
        'author_email',
        'install_requires')
    unils = (
        'packages',
        'classifiers',
        'entry_points',
        'include_dirs',
        'dependency_links')
    names = {
        'web': 'url',
        'modname': 'name',
        'distname': 'name',
        'long_desc': 'long_description'}
    for uni in uniss:
        skwargs[uni] = pinf.get(uni, None)
    for uni in unils:
        skwargs[uni] = pinf.get(uni, [])
    for (key, val) in names.items():
        if key in pinf:
            skwargs[val] = pinf[key]
            if key in skwargs.keys():
                del skwargs[key]
    return skwargs

if __name__ == '__main__':
    __pkginfo__ = {}
    __pkginfo__['packages'] = ['pwclip'] + packages('pwclip')
    with open(path.join('pwclip', '__pkginfo__.py')) as f:
        exec(f.read(), __pkginfo__)
    kwargs = setupkwargs(__pkginfo__)
    if '-v' in argv or '--verbose' in argv:
        print()
        for (k, v) in sorted(kwargs.items()):
            print(k, '=', v)
        print()
    kwargs['package_data'] = {'': ['*.rst']}
    setup(**kwargs)
