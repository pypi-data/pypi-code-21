from setuptools import setup, find_packages

PACKAGE = "BinomialOptnCal"
NAME = "BinomialOptnCal"
DESCRIPTION = "This is a calculator for option pricing based on binomial model."
AUTHOR = "Henry Guo"
AUTHOR_EMAIL = "henryguoziheng@gmail.com"
URL = "https://github.com/timtam12138/OptionCalculator"
VERSION = __import__(PACKAGE).__version__

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    # long_description=read("README.md"),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="Apache License, Version 2.0",
    url=URL,
    packages=['BinomialOptnCal'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    entry_points={
        'console_scripts': [
            ]
    },
    zip_safe=False,
)