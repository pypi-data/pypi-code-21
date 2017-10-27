# coding=utf-8

from setuptools import setup

setup(
  name='webstarts',
  license='BSD',
  description="Entry point for modern flask/gunicorn/sentry/celery web applications",
  long_description="Python entry point setup best practices for modern webapps",
  author='john',
  author_email='john@chaosdevs.com',
  url='https://github.com/j-walker23/webstarts',
  zip_safe=True,
  include_package_data=False,
  packages=['webstarts'],
  use_scm_version=True,
  python_requires='~=3.6',
  setup_requires=[
    'setuptools_scm',
  ],
  install_requires=[
    'semantic_version',
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
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: Version Control',
    'Topic :: System :: Software Distribution',
    'Topic :: Utilities',
  ]
)
