# from distutils.core import setup
import sys
from setuptools import setup, find_packages


install_reqs = [
    'zope.schema==4.4.2',
    'zope.interface==4.3.2',
    'requests',
    'Django',
    'redis',
    'six',
    'lxml',
]

dl = []

if sys.version_info >= (3, 0):
    dl = [
        'https://github.com/stoneworksolutions/suds-py3.git@1.4#egg=suds-1.4',
        'https://github.com/stoneworksolutions/olap.git@0.1#egg=olap-0.1',
    ]
else:
    install_reqs += [
        'suds',
        'olap'
    ]

setup(
    name='eurotools',
    version='0.5.4',
    packages=find_packages(),
    license='',
    long_description=open('README.rst').read(),
    url='http://www.stoneworksolutions.net',
    author='Antonio Palomo Cardenas',
    author_email='antonio.palomo@stoneworksolutions.net',
    package_data={'': ['*.html']},
    include_package_data=True,
    install_requires=install_reqs,
    dependency_links=dl,
)
