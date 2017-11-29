from setuptools import setup

VERSION = '1.0.2'

setup(name = 'numtxt',
      version = VERSION,
      description = 'gives full and approximate written forms of numbers',
      long_description = open('README.rst').read(),
      license = 'GPLv3',
      author = 'Electrostatus',
      url = 'http://github.com/Electrostatus/numtxt',
      py_modules = ['numtxt'],
      keywords = 'approximation written words numbers',
      package_data = {'': ['*.rst']},
      classifiers = [
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Natural Language :: English',
        ],
      )
