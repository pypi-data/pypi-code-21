from distutils.core import setup


setup( name = "mhelper",
       url = "https://bitbucket.org/mjr129/mhelper",
       version = "0.0.0.18",
       description = "Includes a collection of utility functions.",
       author = "Martin Rusilowicz",
       license = "GNU AGPLv3",
       packages = ["mhelper",
                   "mhelper.qt_helpers"],
       install_requires = ["PyQt5"]
       )
