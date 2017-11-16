import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


# with open('requirements.txt') as f:
#     required = f.read().splitlines()


setup(
    # install_requires=required,
    name="sumotools",
    version="0.5",
    description="Redistribution of the SUMO tools modules for use in the TrafficSenseMSD project",
    author="TrafficSenseMSD",
    packages=find_packages(),
    url='https://github.com/TrafficSenseMSD/SumoTools',
    keywords=['sumo', 'traffic', 'simulation']
)
