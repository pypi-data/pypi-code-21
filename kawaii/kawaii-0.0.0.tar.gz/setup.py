from setuptools import (setup,
                        find_packages)

import kawaii
from kawaii.config import PROJECT_NAME

project_base_url = 'https://github.com/lycantropos/kawaii/'

setup_requires = ['pytest-runner>=3.0']
tests_require = [
    'pydevd>=1.1.1',  # debugging
    'pytest>=3.2.1',
    'pytest-cov>=2.5.1',
    'hypothesis>=3.38.5',
]

setup(name=PROJECT_NAME,
      packages=find_packages(exclude=('tests',)),
      version=kawaii.__version__,
      description=kawaii.__doc__,
      long_description=open('README.rst').read(),
      author='Azat Ibrakov',
      author_email='azatibrakov@gmail.com',
      url=project_base_url,
      download_url=project_base_url + 'archive/master.zip',
      setup_requires=setup_requires,
      tests_require=tests_require)
