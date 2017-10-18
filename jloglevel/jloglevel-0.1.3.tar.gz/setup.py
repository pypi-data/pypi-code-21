#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from pip.req import parse_requirements
from jloglevel import __version__


AUTHOR_MAINTAINER = 'Ivan Yurchenko'
AUTHOR_MAINTAINER_EMAIL = 'ivan0yurchenko@gmail.com'


def readme():
    with open('README.md') as f:
        return f.read()


parsed_requirements = parse_requirements(
    'requirements.txt', session='jloglevel_setup')
requirements = [str(r.req) for r in parsed_requirements]

setup(name='jloglevel',
      version=__version__,
      description='A command line tool for changing the logging level '
                  'in JVM apps in runtime via Jolokia',
      long_description=readme(),
      url='https://github.com/ivanyu/jloglevel',
      author=AUTHOR_MAINTAINER,
      author_email=AUTHOR_MAINTAINER_EMAIL,
      maintainer=AUTHOR_MAINTAINER,
      maintainer_email=AUTHOR_MAINTAINER_EMAIL,
      license='Apache 2.0',
      packages=['jloglevel'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: Apache Software License',
          'Topic :: Software Development'
      ],
      zip_safe=True,
      keywords='jmx jolokia logging jvm',
      install_requires=requirements,
      entry_points={
          'console_scripts': ['jloglevel = jloglevel.__main__:cli']
      }
      )
