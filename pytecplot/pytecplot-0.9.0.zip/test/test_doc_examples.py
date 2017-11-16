from __future__ import unicode_literals, print_function

import ctypes
import fnmatch
import inspect
import itertools as it
import logging
import math
import numpy
import numpy as np
import os
import pkgutil
import platform
import random
import re
import sys

from datetime import datetime
from math import sqrt
from os import path
from textwrap import dedent

import unittest

import tecplot
import tecplot as tp
from tecplot.constant import *
from tecplot.exception import *
from tecplot.data.operate import *

from test import skip_on, skip_if_sdk_version_before

doc_ptrn = re.compile(r'((\s*)    import tecplot.*?)(?:^\2\S)', re.M | re.S)
import_from_ptrn = re.compile(r'^\s*from.*?import\s*([(].*?[)]|.*?$)\n', re.M | re.S)
import_ptrn = re.compile(r'\s*import.*')
export_ptrn = re.compile(r'\s*.*?export.*', re.M)

def find_examples(doc):
    """
    searches a string (presumably a doc-string) for complete examples to run.
    The indicator is if the string has an indented "import tecplot" statement.
    All import statements are then stripped out as well as any image export
    statements.
    """
    global doc_ptrn
    global import_ptrn
    global export_ptrn
    for m in doc_ptrn.finditer(doc):
        ex = dedent(m.group(1))
        ex = import_from_ptrn.sub('', ex)
        ex = import_ptrn.sub('', ex)
        ex = export_ptrn.sub('', ex)
        yield ex.strip()

def submodules(module, ignore):
    """
    yields (submodule_name, submodule) pairs for all submodules within
    a given module
    """
    modules = []
    modpath = module.__path__
    modname = module.__name__
    for _,submodule_name,_ in pkgutil.walk_packages(modpath,modname+'.'):
        ignore_this = False
        for i in ignore:
            if fnmatch.fnmatch(submodule_name, i):
                ignore_this = True
        if not ignore_this:
            try:
                submodule = sys.modules[submodule_name]
            except KeyError:
                continue
            yield submodule_name,submodule

def definitions(module_name,module):
    """
    yields all classes and functions directly defined in a given module.
    """
    def isdefinition(obj):
        return inspect.isclass(obj) or inspect.isfunction(obj)
    for member_name,member in inspect.getmembers(module, isdefinition):
        if getattr(member,'__module__',None) == module_name:
            yield member_name,member

def methods(class_, ignore=['__init__', '__weakref__'], inherited=False):
    """
    yields all methods directly defined in a given class.
    """
    def ismember(obj):
        return inspect.ismethod(obj) or inspect.isdatadescriptor(obj) and \
               not inspect.isbuiltin(obj)
    for method_name,method in inspect.getmembers(class_,ismember):
        if method_name not in ignore:
            if inherited or method_name in class_.__dict__:
                yield method_name,method

def object_definitions(module, ignore_modules):
    """
    yields all directly defined (i.e. not imported or inherited) objects
    within the given namespace. This includes modules, classes, functions,
    methods and properties.
    """
    for module_name,module in submodules(module, ignore_modules):
        yield module_name, module
        for member_name,member in definitions(module_name,module):
            member_fullname = '.'.join([module_name,member_name])
            yield member_fullname, member
            for method_name,method in methods(member):
                method_fullname = '.'.join([member_fullname,method_name])
                yield method_fullname, method


class TestDocExamples(unittest.TestCase):
    """
    all doc-example tests will be patched into this class
    """
    def setUp(self):
        if tp.sdk_version_info < (2017, 3):
            raise unittest.SkipTest('example files moved in 2017.3')

ignore_modules = ['*tecutil.constant*', '*exception*']

"""
search the tecplot module for objects which have a doc-string
and which have complete/runable examples within the doc-string
and add the test to the TestDocExamples class.
"""
for objname, obj in object_definitions(tp, ignore_modules):
    doc = obj.__doc__
    if doc:
        for count,ex in enumerate(find_examples(doc)):
            @skip_on(TecplotOutOfDateEngineError)
            def _fn(self, ex=ex):
                tp.new_layout()
                exec(ex)
            attrname = 'test_'+objname.replace('.','_')+'_ex'+str(count)
            #if objname.replace('.','_') == 'tecplot_plot_fieldmap_FieldmapContour':
            #    print(ex)
            setattr(TestDocExamples, attrname, _fn)

if __name__ == '__main__':
    from . import main
    main()
