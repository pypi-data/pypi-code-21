from pathlib import Path

# http://stackoverflow.com/a/27868004/1869370
# from distutils.core import setup
from setuptools import setup

here = Path(__file__).resolve().parent

long_description = Path(here,'README.rst').resolve().read_text()

setup(
    name = 'dowright',
    packages = ['dowright'],
    install_requires=[
        'ruamel.yaml',
        'paramiko',
        'python-digitalocean',
        'memoized_property',
        'gems',
        'tokenmanager',
        'jinja2',
        # 'ansible',
    ],

    version = '0.0.0a7',
    description = ('Simple YAML-based specification for creation and'
                   ' configuration of DigitalOcean droplets'),
    long_description = long_description,
    url = 'https://bitbucket.org/dogwynn/dowright',

    author="David O'Gwynn",
    author_email="dogywnn@acm.org",
    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
    ],
    keywords=('digitalocean yaml specification ansible development'
              ' helper utility'),
)
