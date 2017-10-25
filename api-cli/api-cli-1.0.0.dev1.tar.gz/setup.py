#-*- encoding: UTF-8 -*-
from setuptools import setup, find_packages

setup(
    name = 'api-cli',
    version = '1.0.0.dev1',
    description = "a tiny and smart cli tool for managing api-frame based on Python",
    keywords = 'api-cli api-frame api frame cli python',
    author = 'dzlua',
    author_email = '505544956@qq.com',
    url = 'https://gitee.com/dzlua/api-cli.git',
    license = 'MIT',
    packages = find_packages(),
    include_package_data = True,
    zip_safe = True,
    test_suite = 'tests',
      entry_points={
          'console_scripts': [
              'api-cli = api_cli.main:main'
          ]
      },
    install_requires = [
        '',
    ],
    classifiers = [
        'Development Status :: 1 - Planning',
    ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
)
