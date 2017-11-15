
from setuptools import setup, find_packages
from os.path import join, dirname


setup(
    name="threedb",
    version="1.1",
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    author="Kurochkin Evgeny",
    keywords="ddt testing testdata",
    url="https://github.com/EvgenyAK/3db",
    description="ThreeDB is a lightweight database optimized for data storage used testing",

    install_requires=[
        "pyyaml"
    ],
)
