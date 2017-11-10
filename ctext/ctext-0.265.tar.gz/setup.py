from setuptools import setup
import io

with io.open('README.txt', "r", encoding="utf-8") as file:
    long_desc = file.read()

setup(
    name = "ctext",
    packages = ["ctext"],
    version = "0.265",
    description = "Chinese Text Project API wrapper",
    author = "Donald Sturgeon",
    author_email = "chinesetextproject@gmail.com",
    url = "http://ctext.org/tools/api",
    keywords = ["Chinese", "text", "API", "ctext"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        ],
    long_description = long_desc,
    install_requires = ['requests']
)
