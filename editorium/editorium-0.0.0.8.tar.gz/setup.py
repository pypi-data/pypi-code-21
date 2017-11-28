from distutils.core import setup


setup( name = "editorium",
       url = "https://bitbucket.org/mjr129/editorium",
       version = "0.0.0.8",
       description = "Creates a Qt Editor for arbitrary Python Objects using Reflection.",
       author = "Martin Rusilowicz",
       license = "GNU AGPLv3",
       packages = ["editorium"],
       python_requires = ">=3.6",
       install_requires = ["py-flags",
                           "sip",
                           "PyQt5"]
       )
