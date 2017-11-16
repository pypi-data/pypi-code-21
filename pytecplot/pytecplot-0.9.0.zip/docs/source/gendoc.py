def patch_out_tecutil():
    """
    Patch out loading of DLL so we can
    import tecplot without pulling in
    the tecutilbatch binaries
    """
    from unittest.mock import patch, Mock

    class AutoAttr:
        def __call__(self):
            pass
        def __getattr__(self, attr):
            return self

    no_dlopen_patch = patch('ctypes.cdll.LoadLibrary', Mock(return_value=AutoAttr()))
    no_dlopen_patch.start()

import fnmatch
import os
import pprint
import sys
import yaml

from importlib import import_module
from inspect import *
from os import path
from textwrap import dedent

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
here = os.path.abspath(path.realpath(path.dirname(__file__)))
there = os.path.normpath(path.join(here,'..','..'))
sys.path.insert(0, there)

patch_out_tecutil()
import tecplot

def import_object(objname):
    try:
        return import_module(objname)
    except ImportError:
        try:
            mod, obj = objname.rsplit('.', 1)
            return getattr(import_module(mod), obj)
        except (AttributeError, ValueError):
            raise ImportError

def write_header(fout, title, level):
    uline = '=-^+~'
    fout.write('{}\n{}\n\n'.format(title, uline[level]*len(title)))

def write_ref(fout, name):
    fout.write('.. _{}:\n\n'.format(name))

def write_toc(fout, depth):
    fout.write(dedent('''\
        ..  contents::
            :local:
            :depth: {}

    '''.format(depth)))

def write_object(fout, name, typename, level, **opts):
    if typename in ['function']:
        write_header(fout, name.replace('tecplot.', '')+'()', level)
    elif typename in ['module']:
        write_header(fout, name, level) #.replace('tecplot.', ''), level)
    fout.write('.. auto{}:: {}\n'.format(typename, name))
    directives = ['members', 'inherited-members', 'imported-members',
                  'undoc-members']
    for d in directives:
        if opts.get(d, False):
            fout.write('    :{}:\n'.format(d))
    if typename in ['function', 'module']:
        fout.write('\n')

def write_summary(fout, names, level):
    fmt = '.. autosummary::\n\n    {}\n'
    fout.write(indent('    '*level, fmt.format('\n    '.join(names))))

def filter_names(members, exclude, prefix='', suffix=''):
    ret = []
    for member in members:
        fullname = prefix + member[0] + suffix
        include = True
        for ptrn in exclude:
            if fnmatch.fnmatch(fullname, ptrn):
                include = False
                break
        if include:
            ret.append(member)
    return ret

def write_class(fout, name, level, exclude=[]):
    obj = import_object(name)

    namespace, classname = name.rsplit('.',1)

    methods = getmembers(obj, isfunction)
    methods = filter_names(methods, exclude, prefix=classname + '.')

    def isproperty(x):
        return isdatadescriptor(x) or (not (isfunction(x) or isbuiltin(x)))

    properties = getmembers(obj, isproperty)
    properties = filter_names(properties, exclude, prefix=classname + '.')

    fout.write('.. py:currentmodule:: {}\n\n'.format(namespace))
    write_header(fout, classname, level)
    write_object(fout, classname, 'class', level)

    if properties:
        fout.write('''
    **Attributes**

    .. autosummary::
        :nosignatures:

''')
        names, objs = list(zip(*properties))
        for obj_name, prop in sorted(properties):
            fout.write('        {}\n'.format(obj_name))

    if methods:
        fout.write('''
    **Methods**

    .. autosummary::

''')
        names, objs = list(zip(*methods))
        for obj_name, meth in sorted(methods):
            fout.write('        {}\n'.format(obj_name))
    fout.write('\n')

    def _type(obj):
        if isdatadescriptor(obj):
            return 'attribute'
        if isfunction(obj) or ismethod(obj):
            return 'method'

    if properties or methods:
        attrs = {k: v for k,v in zip(*zip(*(properties + methods)))}
        for attr_name, attr_obj in sorted(attrs.items()):
            attr_path = '.'.join([classname, attr_name])
            t = _type(attr_obj)
            write_object(fout, attr_path, t or 'attribute', level)
            if t is None:
                fout.write('    :annotation:\n')

def write_doc(data, outdir, fout=None, level=0, exclude=[], **opts):
    _tr = dict(fn='function', mod='module', cl='class')
    for i, row in enumerate(data):
        (key, value), = row.items()
        if key == 'exclude':
            exclude = value
        elif key == 'topic':
            assert fout is None, 'can not nest topics.'
            opts = value[0]
            name = opts.pop('name', opts['title']).lower().replace(' ', '_')
            filename = 'tecplot.{}.rst'.format(name)
            rstfile = path.join(outdir, filename)
            with open(rstfile, 'w') as rstout:
                write_doc([{'sec': value}], outdir, rstout, level, exclude=exclude)
        elif key == 'sec':
            if level > 0:
                fout.write('\n')
            opts = value.pop(0)
            for ref in opts.get('aliases', []):
                write_ref(fout, ref)
            write_header(fout, opts['title'], level)
            if 'toc' in opts:
                write_toc(fout, opts['toc'])
            if value:
                write_doc(value, outdir, fout, level+1, exclude=exclude, **opts)
        elif key == 'class':
            if i > 0:
                fout.write('\n')
            write_class(fout, value, level, exclude)
        else:
            write_object(fout, value, _tr[key], level, **opts)


if __name__ == '__main__':
    import filecmp
    import shutil

    from tempfile import TemporaryDirectory

    if len(sys.argv) != 3 or '-h' in sys.argv:
        print('usage: {} {} toc.yaml outdir'.format(sys.executable, sys.argv[0]))
        print('python version 3 (probably) required.')
        sys.exit(-1)

    tocfile, outdir = sys.argv[1:]

    with open(tocfile, 'r') as fin:
        data = yaml.load(fin.read())

    if not path.exists(outdir):
        os.makedirs(outdir)

    with TemporaryDirectory() as dtmp:
        write_doc(data, dtmp)

        for root, dirs, files in os.walk(dtmp):
            for f in files:
                infile = path.join(root, f)
                outfile = path.join(outdir, path.relpath(root, dtmp), f)
                if not (path.exists(outfile) and
                        filecmp.cmp(infile, outfile, shallow=False)):
                    shutil.copy(infile, outfile)
