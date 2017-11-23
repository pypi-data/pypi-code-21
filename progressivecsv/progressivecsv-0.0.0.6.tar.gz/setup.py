from distutils.core import setup


setup( name = "progressivecsv",
       url="https://bitbucket.org/mjr129/progressive_csv",
       version = "0.0.0.6",
       description = "Package for writing a CSV with dynamic headers. CSV is completed at end.",
       author = "Martin Rusilowicz",
       license = "GNU AGPLv3",
       python_requires = ">=3.6",
       packages = [ "progressivecsv" ]
       )
