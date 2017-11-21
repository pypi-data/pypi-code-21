#!/usr/bin/python

import setuptools

setuptools.setup(name             = "MambuPy",
                 version          = "0.6",
                 description      = "A python lib for using Mambu APIs",
                 author           = "Javier Novoa C.",
                 author_email     = "jstitch@gmail.com",
                 license          = "GPL",
                 url              = "https://github.com/jstitch/MambuPy",
                 packages         = ['mambupy',],
                 keywords         = ["mambu",],
                 long_description = """\
                 MambuPy, an API library to access Mambu objects
                 """
                )
