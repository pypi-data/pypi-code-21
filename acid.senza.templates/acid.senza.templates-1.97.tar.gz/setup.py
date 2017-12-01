import inspect
import os
import sys

from setuptools import setup

if sys.version_info < (3, 4, 0):
    sys.stderr.write('FATAL: base template needs to be installed with Python 3.4+\n')
    sys.exit(1)

__location__ = os.path.join(os.getcwd(), os.path.dirname(inspect.getfile(inspect.currentframe())))


def read_version(package):
    data = {}
    with open(os.path.join(package.replace('.', '/'), 'version.py'), 'r') as fd:
        exec(fd.read(), data)
    return data['__version__']


def get_install_requirements(path):
    content = open(os.path.join(__location__, path)).read()
    return [req for req in content.split('\\n') if req != '']


def read(fname):
    return open(os.path.join(__location__, fname)).read()


# https://pypi.python.org/pypi?%3Aaction=list_classifiers
CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Plugins',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: Implementation :: CPython',
    'Topic :: Database'
]

NAME = 'acid.senza.templates'
MAIN_PACKAGE = NAME
VERSION = read_version(MAIN_PACKAGE)
DESCRIPTION = 'Senza template for the automatic PosgreSQL DB deployments'
LICENSE = "Apache License 2.0"
URL = 'https://github.com/zalando-incubator/senza-base-template'
AUTHOR = 'Oleksii Kliukin'
AUTHOR_EMAIL = 'oleksii.kliukin@zalando.de'
KEYWORDS = 'senza postgres'


def setup_packages():

    install_reqs = get_install_requirements('requirements.txt')

    setup(
        name=NAME,
        version=VERSION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        url=URL,
        license=LICENSE,
        keywords=KEYWORDS,
        description=DESCRIPTION,
        packages=[NAME],
        install_requires=install_reqs,
        setup_requires=[
            "flake8"
        ],
        long_description=read('README.rst'),
        entry_points={
            'senza.templates':
                ['base=acid.senza.templates.base']
        }
    )


if __name__ == '__main__':
    setup_packages()
