from distutils.core import setup


setup( name = "bio42",
       url = "https://bitbucket.org/mjr129/bio42",
       version = "0.0.0.16",
       description = "BIO42. Analyser and database manager and for large biological networks stored in Neo4j.",
       author = "Martin Rusilowicz",
       license = "GNU AGPLv3",
       packages = ["bio42",
                   "bio42.helpers",
                   "bio42.plugins",
                   "bio42.plugins.download_terms",
                   "bio42.plugins.parsers"],
       entry_points = { "console_scripts": ["bio42 = bio42.__main__:main"] },
       python_requires = ">=3.6",
       install_requires = ["uniprot",
                           "typing",
                           "py-flags",
                           "colorama",
                           "stringcoercion",
                           "keyring",
                           "progressivecsv",
                           "biopython"]
       )
