from setuptools import setup
from setuptools.command.test import test as TestCommand
import os.path
import sys

import latest


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
    long_description = f.read()


class Tox(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox
        errcode = tox.cmdline(self.test_args)
        sys.exit(errcode)


setup(
    name=latest.__project__,
    version=latest.__release__,
    description='A LaTeX-oriented template engine.',
    long_description=long_description,
    author='Flavio Grandin',
    author_email='flavio.grandin@gmail.com',
    tests_require=[
        'tox',
    ],
    cmdclass = {
        'test': Tox
    },
    install_requires=[
        'pyyaml',
        'pyparsing',
    ],
    include_package_data=True,
    license='MIT',
    url='https://github.com/bluePhlavio/latest',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        ],
    keywords='latex template engine',
    packages=['latest'],
    entry_points={
        'console_scripts': ['latest=latest.__main__:main'],
    },
)


