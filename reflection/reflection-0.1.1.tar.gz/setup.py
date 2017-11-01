try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open("README.rst") as f:
    readme = f.read()

setup(
    name="reflection",
    version="0.1.1",

    description="A modern and pythonic GUI library",
    long_description=readme,

    url="https://github.com/Coal0/reflection",

    author="coal0",
    author_email="charcoalzx@protonmail.com",

    license="MIT",

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: Libraries"
    ],
    keywords=["GUI", "interface", "tkinter", "tk"],

    packages=["reflection"],
)
