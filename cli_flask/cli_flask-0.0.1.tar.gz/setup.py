from distutils.core import setup
import re

def find_version(fname):
    '''Attempts to find the version number in the file names fname.
    Raises RuntimeError if not found.
    '''
    version = ''
    with open(fname, 'r') as fp:
        reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
        for line in fp:
            m = reg.match(line)
            if m:
                version = m.group(1)
                break
    if not version:
        raise RuntimeError('Cannot find version information')
    return version

__version__ = find_version('src/__init__.py')

with open("README.md") as f:
        long_description=f.read()

setup(name='cli_flask',
      version=__version__,
      description='Flask cli (command line interface) for Flask application based project',
      long_description=long_description,
      licence="MIT",
      author='Vijay ',
      author_email='struts2spring@gmail.com',
      url='https://github.com/struts2spring/flask_cli',
      zip_safe=False,
      platforms='any',
      packages=['src', ],
      classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      install_requires=['Click','colorama'],
      scripts=[],
      entry_points={
            'console_scripts':['fl = src.main:cli']
      },

      

     )
