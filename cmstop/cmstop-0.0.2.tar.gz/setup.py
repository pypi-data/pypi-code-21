#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


NAME             = "cmstop"
VERSION          = open("VERSION").read().replace("\n", "")
KEYWORDS         = ("cmstop", "cms", "top", "cmstools")
DESCRIPTION      = "A set tools for cmstop (not release by offical)."
LONG_DRSCRIPTION = open("README.txt").read()
LICENSE          = "MIT LICENSE"
URL              = "https://github.com/teachmyself/icmstop"
AUTHOR           = "teachmyself"
AUTHOR_EMAIL     = "teachmyself@126.com"
PACKAGES         = find_packages()
INSTALL_REQUIRES = open('requirements.txt').readlines()
TEST_SUITE       = ""
SCRIPTS          = []
CONSOLE_SCRIPTS  = [
    "cmstop-find = cmstop.find:main",
]

setup(
    name = NAME,
    version = VERSION,
    keywords = KEYWORDS,
    description = DESCRIPTION,
    long_description = LONG_DRSCRIPTION,
    license = LICENSE,

    url = URL,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,

    packages = PACKAGES,
    install_requires = INSTALL_REQUIRES,
    test_suite = TEST_SUITE,

    scripts = SCRIPTS,
    entry_points = {
        "console_scripts": CONSOLE_SCRIPTS
    }
)
