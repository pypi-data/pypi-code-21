from setuptools import setup

setup(name='chemkin8',
      version='0.3',
      description='A Chemical Kinetics Library',
      url='https://github.com/G8-CS207F17/cs207-FinalProject',
      author='Mehul Smriti Raje, Ruiqi Chen, Ziqi Guo,',
      author_email='zguo@g.harvard.edu',
      license='Harvard',
      packages=['chemkin8'],
      install_requires=['numpy','sqlite3'],
      zip_safe=False)