from setuptools import setup
import pytest_pydev

def read(fname):
    # makes sure that setup can be executed from a different location
    import os.path
    _here = os.path.abspath(os.path.dirname(__file__))
    return open(os.path.join(_here, fname)).read()

setup(
    name='pytest-pydev',
    version=pytest_pydev.__version__,
    author='Sebastian Rahlf',
    author_email='basti@redtoad.de',
    license='MIT License',
    description='py.test plugin to connect to a remote debug server with PyDev or PyCharm.',
    long_description=read('README.rst'),
    url='http://bitbucket.org/basti/pytest-pydev/',
    download_url='http://bitbucket.org/basti/pytest-pydev/downloads/',

    py_modules=['pytest_pydev'],
    entry_points={'pytest11': ['pydev = pytest_pydev']},

    install_requires=[
        'pytest>=2',
    ],

    keywords='py.test, pytest, pydev, pycharm, python remote debugger',
    classifiers=[
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Testing'
    ]
)
