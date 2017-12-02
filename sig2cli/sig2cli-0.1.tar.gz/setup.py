from setuptools import setup

setup(name='sig2cli',
      version='0.1',
      description='Turn function signatures into Command Line Interfaces',
      url='https://github.com/PaoloSarti/sig2cli',
      author='Paolo Sarti',
      author_email='paolo.sarti@gmail.com',
      license='MIT',
      packages=['sig2cli'],
      install_requires=[
          'funcsigs',
      ],
      zip_safe=False)