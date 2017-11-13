#!/usr/bin/env python

from setuptools import setup
from setuptools.command.install import install as _install

class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()

if __name__ == '__main__':
    setup(
        name = 'succubus',
        version = '1.0-224',
        description = '''Lightweight Python module for daemonizing''',
        long_description = '''.. image:: https://travis-ci.org/ImmobilienScout24/succubus.svg
    :alt: Travis build status image
    :align: left
    :target: https://travis-ci.org/ImmobilienScout24/succubus

.. image:: https://coveralls.io/repos/ImmobilienScout24/succubus/badge.svg?branch=master
  :alt: Coverage status
  :target: https://coveralls.io/github/ImmobilienScout24/succubus?branch=master


========
succubus
========

Description
===========
succubus is a lightweight python module for a fast and easy creation of
python daemons and init scripts.

Examples
========

.. code-block:: python

    #!/usr/bin/env python

    import logging
    import sys
    import time

    from logging.handlers import WatchedFileHandler

    from succubus import Daemon


    class MyDaemon(Daemon):
        def run(self):
            """Overwrite the run function of the Daemon class"""
            while True:
                time.sleep(1)
                self.logger.warn('Hello world')

        def setup_logging(self):
            # TODO: don't log to /tmp except for example code
            handler = WatchedFileHandler('/tmp/succubus.log')
            self.logger = logging.getLogger('succubus')
            self.logger.addHandler(handler)


    def main():
        daemon = MyDaemon(pid_file='succubus.pid')
        sys.exit(daemon.action())


    if __name__ == '__main__':
        main()
        
Succubus implements the usual init script actions (start, stop, restart, status) in Python. So your init script can look like this:
        
.. code-block:: bash

    #!/bin/bash
    /usr/bin/my_succubus_daemon $1 --foo=42

If the init script is called as ``/etc/init.d/my_succubus_daemon start``, this will translate into ``/usr/bin/my_succubus_daemon start --foo=42`` being called. The ``start`` parameter is consumed by the succubus framework, i.e. when your code does the command line parsing, it looks as if ``/usr/bin/my_succubus_daemon --foo=42`` was called. You can now parse the ``--foo=42`` parameter as you please.
''',
        author = "Stefan Neben, Stefan Nordhausen",
        author_email = "stefan.neben@immobilienscout24.de, stefan.nordhausen@immobilienscout24.de",
        license = 'Apache License 2.0',
        url = 'https://github.com/ImmobilienScout24/succubus',
        scripts = [],
        packages = ['succubus'],
        py_modules = [],
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Programming Language :: Python'
        ],
        entry_points = {},
        data_files = [],
        package_data = {},
        install_requires = ['psutil'],
        dependency_links = [],
        zip_safe=True,
        cmdclass={'install': install},
    )
