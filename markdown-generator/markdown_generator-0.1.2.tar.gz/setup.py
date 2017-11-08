# -*- coding: utf-8 -*-

from distutils.core import setup


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='markdown_generator',
    version='0.1.2',
    description='Python package for generating GitHub-flavored markdown',
    long_description=readme,
    author='Corey McCandless',
    author_email='crm1994@gmail.com',
    url='https://github.com/cmccandless/markdown-generator',
    license=license,
    packages=['markdown_generator']
#    packages=find_packages(exclude=('tests', 'docs'))
)
