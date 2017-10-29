#-*- coding: utf-8 -*-

from setuptools import setup, find_packages

version = "1.1"

setup(
    name = "django-infinite-pagination-mega",
    version = version,
    description = "Infinite pagination for Django.",
    license = "BSD",

    author = "Filip Wasilewski",
    author_email = "en@ig.ma",

    url = "https://github.com/nigma/django-infinite-pagination",
    download_url="https://github.com/nigma/django-infinite-pagination/zipball/master",

    long_description = open("README.rst").read(),

    packages = find_packages(exclude=["tests"]),
    include_package_data = True,

    tests_require=[
        "django>=1.4,<1.5",
    ],

    classifiers = (
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ),
    zip_safe = False
)
