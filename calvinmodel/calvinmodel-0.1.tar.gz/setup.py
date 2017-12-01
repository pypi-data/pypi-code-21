from setuptools import setup

setup(name='calvinmodel',
      version='0.1',
      description='A package with models of the Calvin Cycle',
      url='https://gitlab.com/ebenhoeh/calvinmodel',
      author='Oliver Ebenhoeh',
      author_email='oliver.ebenhoeh@hhu.de',
      license='GPL4',
      packages=['calvinmodel'],
      install_requires=[
          'numpy',
          'scipy',
          'modelbase>=0.1.6',
          'matplotlib'
          #'itertools',
          #'re',
          #'pickle'
      ],
      zip_safe=False)
