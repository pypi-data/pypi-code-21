
import os
from setuptools import setup
from setuptools import find_packages

PACKAGE = "pyesp"

print(__import__(PACKAGE).__version__)
setup(
    name=PACKAGE,
    version=__import__(PACKAGE).__version__,
    author="Vladislav Kamenev",
    author_email="wladkam@mail.com",
    url="https://github.com/LeftRadio/pyesp",
    description="tool for programming/comunicate with ESP8266 platforms based on MircoPython and NodeMCU",
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    package_data={
        PACKAGE: [
            'data/api/*.json',
            'data/serial/*.json'
        ]
    },
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pyesp = pyesp.run : main'
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Utilities',
        'Programming Language :: Python :: 3',
    ],
    license='MIT'
)
