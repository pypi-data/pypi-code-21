from setuptools import setup, find_packages
import sys, os

version = '0.1.4.0'

setup(name='pyprogress',
      version=version,
      description="Various command line progress bars, spinners and counters including threaded versions",
      long_description="""\
""",
      classifiers=[
          'Environment :: Console',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.0',
          'Programming Language :: Python :: 3.1',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
      ],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='progress spinner counter cli timer completion',
      author='Graham Moucka',
      author_email='mouckatron@gmail.com',
      url='https://github.com/mouckatron/pyprogress',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      test_suite='tests',
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points={
          'console_scripts': [
              'countoutput = pyprogress.countoutput:main',
          ]
      },
      )
