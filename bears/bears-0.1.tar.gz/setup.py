from setuptools import setup

LONG_DESCRIPTION = """
**bears** is a light alternative to pandas. Its main goal is to provide a columnar dataframe.
Dataframe is a collection of columns. Each column is a numpy.ndarray.

The difference from pandas is as follows:
- no fancy indexing
- no label index / no active column
- no implicit copy / expensive operation

You can
- add/remove a column in O(1)
- slice indexing / list indexing without copy
- transpose the columnar dataframe to get the record-wise list 
"""

setup(name='bears',
      version='0.1',
      description='simpler and faster alternative to pandas',
      long_description=LONG_DESCRIPTION,
      classifiers=[
          'Operating System :: OS Independent',
          'Intended Audience :: Science/Research',
          'Programming Language :: Python :: 3.6',
          'Topic :: Scientific/Engineering'
      ],
      url='http://github.com/elbaro/bears',
      author='elbaro',
      author_email='elbaro@users.noreply.github.com',
      license='MIT',
      packages=['bears'],
      zip_safe=False)
