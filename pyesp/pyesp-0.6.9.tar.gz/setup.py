
import os
from setuptools import setup
from setuptools import find_packages

PACKAGE = "pyesp"

dirname = os.path.dirname(__file__)

setup(
    name=PACKAGE,
    version=__import__(PACKAGE).__version__,
    author="Vladislav Kamenev",
    author_email="wladkam@mail.com",
    url="https://github.com/LeftRadio/pyesp",
    description="tool for programming/comunicate with ESP8266 platforms based on MircoPython and NodeMCU",
    long_description=open(os.path.join(dirname, 'README.md')).read(),
    package_data={
        PACKAGE: [
            os.path.join(
                os.path.join(dirname, os.path.dirname(__import__(PACKAGE).__api_mpy_path__))
            , "*.json"),
            os.path.join(
                os.path.join(dirname, os.path.dirname(__import__(PACKAGE).__serial_config_path__))
            , "*.json"),
        ]
    },
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "pyesp = pyesp.run : main"
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Utilities',
        'Programming Language :: Python :: 3',
    ],
    license='MIT'
)
