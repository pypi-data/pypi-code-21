from distutils.core import setup


setup( name = "neocommand",
       version = "0.0.0.2",
       description = "intermake extension for creating Neo4j driven applications.",
       author = "Martin Rusilowicz",
       license = "GNU AGPLv3",
       packages = [ "neocommand" ],
       entry_points= { "console_scripts": [ "neocommand = neocommand.__main__:main" ] }
       )
