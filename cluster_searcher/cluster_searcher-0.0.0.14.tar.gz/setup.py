from distutils.core import setup

setup( name = "cluster_searcher",
       url="https://bitbucket.org/mjr129/cluster_searcher",
       version = "0.0.0.14",
       description = "Searches a specific file.",
       author = "Martin Rusilowicz",
       license = "GNU AGPLv3",
       packages = [ "cluster_searcher" ],
       entry_points= { "console_scripts": [ "cluster_searcher = cluster_searcher.__main__:main" ] },
       install_requires = ["colorama", 
                           "intermake",
                           "mhelper" ]
       )
