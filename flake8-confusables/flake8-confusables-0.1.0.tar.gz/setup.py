import os.path
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))


def get_long_description():
    with open(os.path.join(here, 'README.rst')) as f:
        return f.read()


def get_version():
    with open(os.path.join(here, 'flake8_confusables.py')) as f:
        for line in f:
            if line.startswith('__version__'):
                return eval(line.split('=')[-1])


setup(
    name='flake8-confusables',
    version=get_version(),
    description='A flake8 plugin to check for ambiguous identifiers',
    long_description=get_long_description(),
    url='https://gitlab.com/dirn/flake8-confusables',
    author='Andy Dirnberger',
    author_email='andy@dirnberger.me',
    keywords='flake8, confusables, ambiguity',
    license='MIT',
    py_modules=['flake8_confusables'],
    install_requires=[
        # TODO(dirn): Set a minimum version requirement once this
        # properly installs cython.
        'confusables',
        # This is required by confusables. The most recent release
        # (0.5.800) tries to use it during installation and fails if it
        # isn't already installed. The fix is available in the source,
        # so any future releases of confusables should take care of
        # this.
        'cython',
        'flake8 > 3.0.0',
    ],
    entry_points={
        'flake8.extension': {
            'C001 = flake8_confusables:IdentifierChecker',
        },
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Framework :: Flake8',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Quality Assurance',
    ],
)
