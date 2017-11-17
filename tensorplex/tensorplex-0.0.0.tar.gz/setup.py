import os
from setuptools import setup

from _name import NAME

def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(name=NAME,
      version='0.0.0',
      author='Jim Fan',
      description='{} library.'.format(NAME),
      long_description=read('README.rst'),
      license='GPLv3',
      packages=[NAME],
      classifiers=[
          "Development Status :: 1 - Planning",
          "Programming Language :: Python :: 3"
      ],
      # install_requires=read('requirements.txt').strip().splitlines(),
      # include_package_data=True,
      # zip_safe=False
)
