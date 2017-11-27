#! python3
# Help from: http://www.scotttorborg.com/python-packaging/minimal.html
# https://docs.python.org/3.4/tutorial/modules.html
# Install it with python setup.py install
# Or use: python setup.py develop (changes to the source files will be immediately available)

from setuptools import setup

setup(name='invpy_libs',
      version='0.4.2',
      description='Inventory automation libraries servers list',
      url='https://github.com/pablodav/invpy_libs.git',
      author='Pablo Estigarribia',
      author_email='pablodav@gmail.com',
      license='gplv3',
      packages=['invpy_libs'],
      install_requires=[
          'openpyxl',
      ],
      zip_safe=False)
