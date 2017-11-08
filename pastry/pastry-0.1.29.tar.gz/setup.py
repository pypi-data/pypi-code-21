import os

try:
    from setuptools import setup, find_packages
    from setuptools.command.test import test as TestCommand
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages
    from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ''

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import sys
        import pytest
        errno = pytest.main(self.pytest_args.split(' '))
        sys.exit(errno)

install_requires = [
    'rsa',
    'pyyaml',
    'requests'
]

tests_require = [
    'mock',
    'pytest-cov',
    'coverage',
    'pytest'
]

setup(
    name='pastry',
    version='0.1.29',
    description='A simple api wrapper for chef',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    author='Stephen Breyer-Menke',
    author_email='steve.bm@gmail.com',
    license='MIT',
    url='https://github.com/stephenbm/pastry',
    packages=find_packages(),
    test_suite='tests',
    tests_require=tests_require,
    cmdclass={'test': PyTest},
    install_requires=install_requires,
    include_package_data=True,
    zip_safe=False
)
