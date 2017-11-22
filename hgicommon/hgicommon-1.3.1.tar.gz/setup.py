from setuptools import setup, find_packages

try:
    from pypandoc import convert
    def read_markdown(file: str) -> str:
        return convert(file, "rst")
except ImportError:
    def read_markdown(file: str) -> str:
        return open(file, "r").read()

setup(
    name="hgicommon",
    version="1.3.1",
    author="Colin Nolan",
    author_email="colin.nolan@sanger.ac.uk",
    packages=find_packages(exclude=["tests"]),
    install_requires = [x for x in open("requirements.txt", "r").read().splitlines()],
    url="https://github.com/wtsi-hgi/python-common",
    license="LGPL",
    description="Common Python code used in HGI projects.",
    long_description=read_markdown("README.md"),
    test_suite="hgicommon.tests",
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)"
    ]
)
