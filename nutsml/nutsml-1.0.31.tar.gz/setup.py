import os
import sys
import glob
import shutil
import nutsml

from setuptools import setup, find_packages, Command
from setuptools.command.test import test as TestCommand


class CleanCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        for folder in ['build', 'dist']:
            if os.path.exists(folder):
                shutil.rmtree(folder)
        for egg_file in glob.glob('*egg-info'):
            shutil.rmtree(egg_file)


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


setup(
    name='nutsml',
    version=nutsml.__version__,
    url='https://maet3608.github.io/nuts-ml',
    download_url='https://github.com/maet3608/nuts-ml',
    license='Apache Software License (http://www.apache.org/licenses/LICENSE-2.0)',
    author='Stefan Maetschke',
    author_email='stefan.maetschke@gmail.com',
    description='Flow-based data pre-processing for Machine Learning',
    install_requires=[
        'six >= 1.10.0',
        'nutsflow >= 1.0.25',
        'pyyaml >= 3.12',
        'xlrd >= 1.0.0',
        'dplython >= 0.0.7',
        'numpy >= 1.11.1',
        'matplotlib >= 1.5.1',
        'scipy >= 0.17.0',
        'pillow >= 3.0.0',
        'scikit-image >= 0.12.3',
        'pandas >= 0.18.1',
        'pytest >= 3.0.3',
    ],
    tests_require=['pytest >= 3.0.3'],
    platforms='any',
    packages=find_packages(exclude=['setup']),
    include_package_data=True,
    cmdclass={
        'test': PyTest,
        'clean': CleanCommand,
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
)
