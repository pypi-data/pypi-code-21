
from setuptools import setup, find_packages
from os.path import join, dirname


setup(
    name="threedb",
    version="1.0",
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
    author="Kurochkin Evgeny",
    keywords="ddt testing testdata",
    url="https://github.com/EvgenyAK/3db",

    install_requires=[
        "pyyaml",
    ],
)
