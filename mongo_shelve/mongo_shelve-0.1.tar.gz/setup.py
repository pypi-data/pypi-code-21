#!/usr/bin/python3.5

from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='mongo_shelve',
      version='0.1',
      description='Persistent dictionaries based on mongoDB',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Topic :: Database',
      ],
      keywords='shelve persistent dictionary',
      url='https://github.com/zeycus/mongo_shelve/',
      author='Miguel Garcia Diaz (aka Zeycus)',
      author_email='zeycus@gmail.com',
      license='MIT',
      packages=['mongo_shelve'],
      install_requires=[
      ],
      include_package_data=True,
      zip_safe=False,
      test_suite='nose.collector',
      tests_required=['nose'],
)
