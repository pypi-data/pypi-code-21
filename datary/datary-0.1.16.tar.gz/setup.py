import os
import sys
from setuptools import setup, find_packages
from pip.req import parse_requirements

install_reqs = parse_requirements('requirements.txt', session=False)
required = [str(ir.req) for ir in install_reqs]

_here = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, _here)


def version():
    import imp
    path = os.path.join(_here, 'datary', 'version.py')
    mod = imp.load_source('version', path)
    return mod.__version__

setup(
    name='datary',
    packages=find_packages(),
    version=version(),
    description='Datary Python sdk lib',
    author='Datary developers team',
    author_email='support@datary.io',
    url='https://github.com/Datary/python-sdk',
    download_url='https://github.com/Datary/python-sdk',
    keywords=['datary', 'sdk', 'api'],  # arbitrary keywords
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ],
    install_requires=required,
)
