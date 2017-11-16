from distutils.core import setup


setup( name = "mautoinstall",
       url = "https://bitbucket.org/mjr129/mautoinstall",
       version = "0.0.0.44",
       description = "Install helper for my apps with a friendlyish command-line UI.",
       author = "Martin Rusilowicz",
       license = "GNU AGPLv3",
       packages = ["mautoinstall"],
       entry_points = { "console_scripts": ["mautoinstall = mautoinstall.__main__:main"] },
       install_requires = ["typing"]
       )
