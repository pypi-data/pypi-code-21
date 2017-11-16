
from version import __version__
from setuptools import setup


setup(name='Dero',
      version=__version__,
      description="Nick DeRobertis Personal Library",
      long_description='''
      Nick DeRobertis' personal library of functions. This is hosted on PyPi mostly for my own 
      convenience, though others may use it so long as I'm given credit. 
      ''',
      author='Nick DeRobertis',
      author_email='whoopnip@gmail.com',
      license='MIT',
      packages=['dero'],
      classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
        ],
       install_requires=[
        'pandas',
        'pandasql',
        'numpy',
        'wrds',
        'pdfrw',
        'selenium',
        'unidecode',
        'IPython',
        'sas7bdat',
        'statsmodels',
        'matplotlib',
        'sympy',
        'pandastable'],
     )