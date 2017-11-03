#!/usr/bin/env python
from setuptools import setup

version = '1.8.1'

classifiers = ["Development Status :: 5 - Production/Stable",
               "License :: OSI Approved :: Apache Software License",
               "Programming Language :: Python",
               "Programming Language :: Python :: 2.6",
               "Programming Language :: Python :: 2.7",
               "Programming Language :: Python :: 3.2",
               "Programming Language :: Python :: 3.3",
               "Programming Language :: Python :: 3.4",
               "Programming Language :: Python :: 3.5",
               "Programming Language :: Python :: 3.6",
               "Programming Language :: Python :: Implementation :: PyPy"]

setup(name='timestring-pleasantone',
      version=version,
      description="Human expressed time to Dates and Ranges",
      long_description="""
[Fork and active maintenance of github.com/stevepeak/timestring.]

Converting natural language strings into representable time via
Date and Range objects and features to compare and adjust
Dates and Ranges. Dates and Ranges contain datetime compatible
objects inside them to allow for easy integration into legacy
code.
""",
      classifiers=classifiers,
      keywords='date time range datetime datestring',
      author='@stevepeak, @pleasantone (fork)',
      author_email='steve@stevepeak.net',
      url='http://github.com/pleasantone/timestring',
      license='http://www.apache.org/licenses/LICENSE-2.0',
      packages=['timestring'],
      include_package_data=True,
      zip_safe=True,
      install_requires=["pytz", "word2number"],
      entry_points={'console_scripts': ['timestring=timestring:main']})
