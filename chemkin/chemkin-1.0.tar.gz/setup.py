
from setuptools import setup,find_packages

setup(name='chemkin',
      version='1.0',
      description='The best chemkin package',
      url='https://github.com/G12-cs207-FinalProject/cs207-FinalProject.git',
      author='Parser',
      license='Harvard',
      #this does not work
      packages=['chemkin', 'chemkin.preprocessing', 'chemkin.reaction', 'chemkin.thermodynamics']
)