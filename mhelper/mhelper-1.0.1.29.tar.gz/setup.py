from distutils.core import setup


setup( name = "mhelper",
       url = "https://bitbucket.org/mjr129/mhelper",
       version = "1.0.1.29",
       description = "Includes a collection of utility functions.",
       author = "Martin Rusilowicz",
       license = "GNU AGPLv3",
       packages = ["mhelper",
                   "mhelper.qt_helpers"],
       python_requires = ">=3.6",
       install_requires = ["PyQt5"]
       )
