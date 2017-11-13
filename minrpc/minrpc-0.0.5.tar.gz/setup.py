"""
Installation script for minrpc.

Usage:
    python setup.py install
"""

from setuptools import setup
from distutils.util import convert_path


def read_file(path):
    """Read a file in binary mode."""
    with open(convert_path(path), 'rb') as f:
        return f.read()


def exec_file(path):
    """Execute a python file and return the `globals` dictionary."""
    namespace = {}
    exec(read_file(path), namespace, namespace)
    return namespace


def get_long_description():
    """Compose a long description for PyPI."""
    long_description = None
    try:
        long_description = read_file('README.rst').decode('utf-8')
        long_description += '\n' + read_file('COPYING.rst').decode('utf-8')
        long_description += '\n' + read_file('CHANGES.rst').decode('utf-8')
    except (IOError, UnicodeDecodeError):
        pass
    return long_description


def get_setup_args():
    """Accumulate metadata for setup."""
    long_description = get_long_description()
    metadata = exec_file('minrpc/__init__.py')
    return dict(
        name='minrpc',
        version=metadata['__version__'],
        description=metadata['__summary__'],
        long_description=long_description,
        author=metadata['__author__'],
        author_email=metadata['__author_email__'],
        url=metadata['__uri__'],
        license=metadata['__license__'],
        classifiers=metadata['__classifiers__'],
        packages = [
            "minrpc",
        ],
        include_package_data=True, # include files matched by MANIFEST.in
        install_requires=[
            'setuptools',
        ],
    )


def main():
    """Execute setup with parameters from ``sys.argv``."""
    setup_args = get_setup_args()
    setup(**setup_args)


if __name__ == '__main__':
    main()
