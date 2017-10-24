# coding=utf-8

from setuptools import find_packages, setup

setup(
  name='webstarts',
  license='BSD',
  description="Entry point for modern flask/gunicorn/sentry/celery web applications",
  long_description="Python entry point setup best practices for modern webapps",
  author='john',
  author_email='john@chaosdevs.com',
  url='https://github.com/j-walker23/webstarts',
  zip_safe=False,
  include_package_data=True,
  packages=find_packages(exclude=('wstests',)),
  use_scm_version=True,
  setup_requires=['setuptools_scm', 'semantic_version'],
  python_requires='~=3.6',
  install_requires=[
    'click',
    'celery>=4.0.2',
    'colorama>=0.3.9',
    'decorator>=4.0.11',
    'flask>=0.12.2',
    'flask-sqlalchemy>=2.3',
    'gevent>=1.2.2',
    'gunicorn>=19.7.1',
    'kids.cache>=0.0.4',
    'raven[flask]>=6.1.0',
    'requests>=2.18.1',
    'sqlalchemy>=1.1.11',
    'structlog>=17.2.0',
  ],
  entry_points='''
    [console_scripts]
    webstarts=webstarts:entry
    webstarts.cli=cli:cli
  ''',
  classifiers=[
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3.6',
    'Topic :: Software Development',
  ]
)
