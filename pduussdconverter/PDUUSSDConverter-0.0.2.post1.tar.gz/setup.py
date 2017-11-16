import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="PDUUSSDConverter",
    version="0.0.2post1",
    author="Saviour Gidi",
    author_email="profsaviour@gmail.com",
    description="A utility to convert between pdu, gsm codes, \
    ussd and string formats",
    license="MIT",
    keywords="PDU USSD GSM HEX",
    url="https://github.com/saviour123/PDU-USSDConverter.git",
    packages=['PDUUSSDConverter'],
    long_description=read('README.md'),
    install_requires=[],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)
