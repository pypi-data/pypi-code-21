from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Neweshy',
    version='2.0.4',

    description='A sample Python project',
    long_description="",
    url='https://github.com/pypa/sampleproject',

    author='Mahmoud ElNeweshy',
    author_email='mahmoud.elneweshy@nagwa.com',

    # Choose your license
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],


    py_modules=["Neweshy"],

)