from setuptools import setup
import os

requirements = os.path.join(os.path.dirname(__file__), 'requirements.txt')

setup(
    name='uvhue',
    version='0.4',
    description='Hue client for uvhttp',
    url='https://github.com/justinbarrick/uvhue',
    packages=['uvhue'],
    install_requires=[ r.rstrip() for r in open(requirements).readlines() ]
)
