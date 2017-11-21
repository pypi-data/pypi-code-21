import os
from distutils.core import setup

from setuptools import find_packages

root_dir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(root_dir, "VERSION")) as f:
    VERSION = f.read().rstrip()

setup(
    name='mkdjango',

    version=VERSION,

    install_requires=[
        'django>=1.10'
    ],

    packages=find_packages(),

    url='https://github.com/MichaelKim0407/mkdjango',

    license='MIT',

    author='Michael Kim',

    author_email='mkim0407@gmail.com',

    description='',

    classifiers=[
        "Development Status :: 1 - Planning",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: MIT License",

        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",

        "Topic :: Software Development :: Libraries"
    ]
)
