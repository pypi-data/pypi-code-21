from setuptools import setup
import os
import sys

def readme():
    thefile = open('docs/README.rst')
    return thefile.read()

if sys.argv[-1] == 'travis':
    result = os.system("python crickit/PlayCricket.py")
    if result:
        result = os.system("python crickit/simulate.py")
    if result:
        result = os.system("python crickit/tests/tests.py")
    if result == 0:
        os.system("coverage run crickit/simulate.py")
        os.system("coverage report")
        # os.system("python setup.py sdist upload")
    sys.exit()

setup(
    name='crickit',
    version='0.0.125',
    packages=['crickit'],
    url="https://github.com/oficiallyAkshayEdu/crickit",
    license='MITa',
    author='Akshay Agrawal',
    author_email='',
    description='Text based Cricket Simulator in Python',
    long_description = readme(),
    install_requires=[]
)

