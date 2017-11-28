#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import setuptools
import pypandoc

def read(*paths):
    with open(os.path.join(*paths), "r") as filename:
        return filename.read()

def main():

    setuptools.setup(
        name             = "supermodule",
        version          = "2017.11.28.1622",
        description      = "super utilities",
        #long_description = (read("README.md")),
        long_description = pypandoc.convert("README.md", "rst"),
        url              = "https://github.com/wdbm/junk",
        author           = "John Drake",
        author_email     = "j.drake@sern.ch",
        license          = "GPLv3",
        py_modules       = ["supermodule"],
        entry_points     = """
                           [console_scripts]
                           supermodule = supermodule:supermodule
                           superdupermodule = superdupermodule:superdupermodule
                           """
    )

if __name__ == "__main__":
    main()
