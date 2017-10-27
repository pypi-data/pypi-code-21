from setuptools import setup

setup(name='gaps_dataset',
      version='1.1.4',
      description='Download script for GAPs deep learning dataset from TU Ilmenau',
      url='http://www.tu-ilmenau.de/neurob/data-sets-code/gaps/',
      author='Markus Eisenbach',
      author_email='markus.eisenbach@tu-ilmenau.de',
      license='(for academic use only)',
      packages=['gaps_dataset'],
	  install_requires=['numpy'],
      zip_safe=False)
