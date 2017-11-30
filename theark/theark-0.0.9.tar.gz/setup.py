import os
from setuptools import setup


def readme():
    try:
        with open("readme.md") as f:
            return f.read()
    except:
        return ""

setup(
    name="theark",
    version="0.0.9",
    author="meltmedia QA Team",
    author_email="qa-d@meltmedia.com",
    description="meltQA Tools Common Library.",
    license="Apache Software License",
    keywords="selenium helpers qa automation",
    url="https://github.com/meltmedia/the-ark",
    packages=['the_ark', 'the_ark.resources'],
    long_description=readme(),
        install_requires=[
        "boto >= 2.29.1",
        "requests >= 2.3.0",
        "selenium >= 2.53.0"
    ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Topic :: Utilities",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: Apache Software License",
    ],
)
