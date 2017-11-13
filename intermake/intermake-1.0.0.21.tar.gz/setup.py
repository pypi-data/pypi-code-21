from distutils.core import setup


setup( name = "intermake",
       version = "1.0.0.21",
       description = "Automated run-time generation of user interfaces from Python code - command-line-args, CLI, python-interactive, python-scripted, graphical (Qt GUI)",
       author = "Martin Rusilowicz",
       license = "AGPLv3",
       url = "https://bitbucket.org/mjr129/intermake",
       packages = ["intermake",
                   "intermake.datastore",
                   "intermake.engine",
                   "intermake.helpers",
                   "intermake.hosts",
                   "intermake.hosts.frontends",
                   "intermake.hosts.frontends.gui_qt",
                   "intermake.hosts.frontends.gui_qt.designer",
                   "intermake.hosts.frontends.gui_qt.views",
                   "intermake.plugins",
                   "intermake.visualisables"],
       install_requires = ["colorama",
                           "stringcoercion",
                           "editorium",
                           "py-flags"
                           "mhelper",
                           "PyQt5"]
       )
