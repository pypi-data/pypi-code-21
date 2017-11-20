from setuptools import setup, find_packages

PACKAGE = "xclarity_client"
NAME = "python-xclarityclient"
DESCRIPTION = "This is a Python library for controlling XClarity by REST API. "
AUTHOR = "Finix Lei"
AUTHOR_EMAIL = "leilei4@lenovo.com"
# URL = "http://www.lenovo.com.cn/"
VERSION = __import__(PACKAGE).__version__

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    # long_description=read("README.md"),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="Apache License, Version 2.0",
    # url=URL,
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    entry_points={
        'console_scripts': [
            'python_xclarityclient = python_xclarityclient:main',
            ]
    },
    zip_safe=False,
)
