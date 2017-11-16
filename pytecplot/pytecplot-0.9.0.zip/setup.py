from __future__ import print_function

import os
import platform
import re
import sys
from codecs import open
from os import path
from subprocess import Popen, PIPE
from textwrap import dedent

SUPPORTED_PYTHON_VERSIONS = [(2,7), (3,4), (3,5), (3,6)]

def long_description():
    here = path.abspath(path.dirname(__file__))
    with open(path.join(here,'README.rst'), encoding='utf-8') as f:
        return f.read()

def read_version():
    here = path.abspath(path.dirname(__file__))
    with open(path.join(here,'tecplot','version.py'), encoding='utf-8') as f:
        m = re.search(r"version = '(.*?)'",f.read(),re.M)
        return m.group(1)

def write_coveragerc(filename):
    fmt = dedent("""\
        [report]
        # Regexes for lines to exclude from consideration
        exclude_lines =
            pragma: no cover
        {pyver}
        {system}
            if 0:
            if False:
            if __name__ == .__main__.:

        omit =
            tecplot/tecutil/constant.py
            tecplot/tecutil/sv.py
            tecplot/tecutil/tecutil.py
            tecplot/tecutil/tecutil_rpc.py
            tecplot/tecutil/tecrpc
    """)

    opts = {}

    version = sys.version_info[:2]
    assert version in SUPPORTED_PYTHON_VERSIONS

    pyver = ''
    def vinfo(op, v):
        s = '        if sys\.version_info {op} \({v}\n'
        return s.format(op=op, v=', '.join(str(x) for x in v))
    for v in sorted(set(x[0] for x in SUPPORTED_PYTHON_VERSIONS)):
        if v < version[0]:
            pyver += vinfo('<=?', [v])
        elif v == version[0]:
            pyver += vinfo('[<>]', [v])
            for vv in sorted(filter(lambda x: x[0]==v,
                                    SUPPORTED_PYTHON_VERSIONS)):
                if vv < version:
                    pyver += vinfo('<=?', vv)
                elif vv == version:
                    pyver += vinfo('[<>]', vv)
                else:
                    pyver += vinfo('>=?', vv)
        else:
            pyver += vinfo('>=?', [v])
    opts['pyver'] = pyver

    lin = '[Ll]inux'
    win = '[Ww]indows'
    mac = '[Dd]arwin'
    if platform.system() == 'Windows':
        target = win
        others = (lin,mac)
    elif platform.system() == 'Darwin':
        target = mac
        others = (win,lin)
    else: #if platform.system() == 'Linux':
        target = lin
        others = (win,mac)

    opts['system'] = """\
    if platform\.system.*(?!{0})

    def.*{1}.*(?!{0})
    def.*(?!{0}).*{1}
    def.*{2}.*(?!{0})
    def.*(?!{0}).*{2}
""".format(target,*others)

    with open(filename, 'w') as fout:
        fout.write(fmt.format(**opts))

def install_requires():
    req = ['six', 'pyzmq', 'flatbuffers']
    if sys.version_info < (3,0):
        req.append('future')
        req.append('contextlib2')
    if sys.version_info < (3,4):
        req.append('enum34')
    return req

def test_requires():
    req = ['coverage']
    if sys.version_info < (3,3):
        req.append('mock')
    return req

def extra_requires():
    return ['numpy', 'ipython', 'pillow']

def doc_requires():
    req = ['sphinx', 'sphinxcontrib-napoleon']
    if sys.version_info < (3,3):
        req.append('mock')
    return req

def setup_opts():
    from setuptools import find_packages
    opts = dict(
        name='pytecplot',
        version=read_version(),
        description='A python interface to Tecplot 360 EX',
        long_description=long_description(),
        #url='http://www.tecplot.com/pytecplot',
        url='http://www.tecplot.com/docs/pytecplot',
        author='Tecplot, Inc.',
        author_email='support@tecplot.com',
        #license='',
        classifiers=[
            # Development Status
            #   1 - Planning
            #   2 - Pre-Alpha
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Intended Audience :: Education',
            'Intended Audience :: End Users/Desktop',
            'Intended Audience :: Science/Research',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Topic :: Education',
            'Topic :: Multimedia :: Graphics :: 3D Rendering',
            'Topic :: Multimedia :: Graphics :: Presentation',
            'Topic :: Multimedia :: Graphics :: Viewers',
            'Topic :: Scientific/Engineering',
            'Topic :: Scientific/Engineering :: Information Analysis',
            'Topic :: Scientific/Engineering :: Mathematics',
            'Topic :: Scientific/Engineering :: Physics',
            'Topic :: Scientific/Engineering :: Visualization',
            'Topic :: Software Development :: Libraries',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'License :: Other/Proprietary License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
        ],
        keywords= [
            'tecplot',
            'cfd',
            'data analysis',
            'scientific',
            'scientific computing',
            'statistics',
            'visualization',
            'numerical simulation',
            'aerospace',
        ],
        packages=find_packages(exclude=['test', 'test*']),
        install_requires=install_requires(),
        extras_require={
            'extras' : extra_requires(),
            'doc' : doc_requires(),
            'test' : test_requires(),
            'all' : extra_requires() + doc_requires() + test_requires(),
        },
    )
    return opts

if __name__ == '__main__':
    import struct

    version = sys.version_info[:2]
    if version < SUPPORTED_PYTHON_VERSIONS[0]:
        err = 'PyTecplot only supports Python versions {} and {}+'
        vs = ['.'.join(str(i) for i in v) for v in SUPPORTED_PYTHON_VERSIONS[:2]]
        raise Exception(err.format(*vs))

    pointer_size = struct.calcsize('P')
    if pointer_size != 8:
        err = 'ERRROR: {} bit architecture detected.\n'.format(pointer_size*8)
        err += 'PyTecplot must be used with a 64-bit version of Python.'
        raise Exception(err)

    try:
        write_coveragerc('.coveragerc')
    except OSError:
        log.info('Could not write .coveragerc file.')

    from setuptools import setup
    setup(**setup_opts())
