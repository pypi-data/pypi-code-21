try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open("README.rst") as f:
    readme = f.read()

setup(
    name="backtrack",
    version="1.0.0",

    description="Simple logging in Python 3.",
    long_description=readme,

    url="https://github.com/Coal0/backtrack",

    author="coal0",
    author_email="charcoalzx@protonmail.com",

    license="MIT",

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: System :: Logging"
    ],
    keywords=["log", "logging", "logger"],

    packages=["backtrack"],
)
