# -*- coding: utf-8 -*-
import sys

import invoke
from dkfileutils.which import get_executable

from dktasklib.utils import win32
from dktasklib import runners


class MissingCommand(Exception):
    """Exception thrown when a command (executable) is not found.
    """
    pass


# noinspection PyShadowingNames
class Executables(object):
    """Class for finding executables on the host system.
    """
    def __init__(self):
        self._cache = {}
        self._ctx = None

    @property
    def ctx(self):
        if self._ctx is None:
            self._ctx = invoke.Context()
        return self._ctx

    def require(self, *dependencies):
        """Ensure that all dependencies are available.
           You should not need to call this yourself, use the :func:`requires`
           decorator instead.
        """
        for dep in dependencies:
            self.find(dep)

    def find(self, name, requires=(), install_txt=''):
        """Find the executable named ``name`` on the :envvar:`PATH`.

           Args:
               name (str):
                    name of executable to find.
               requires (List[str]):
                    list of executables to find first.
               install_txt (str):
                    instructions for how to install the
                    executable if it is not found.
        """
        if name not in self._cache:
            self.require(*requires)

            if hasattr(self, 'find_' + name):
                self._cache[name] = getattr(self, 'find_' + name)()
            else:
                self._cache[name] = self._find_exe(name, requires, install_txt)
        return self._cache[name]

    def _find_exe(self, name, requires=(), install_txt=None):
        fexe = get_executable(name)
        if not fexe:  # pragma: nocover
            if not install_txt:  # pragma: nocover
                install_txt = "Missing command: %r" % name
                if requires:
                    install_txt += " [requires: %s]" % requires
            raise MissingCommand(install_txt)
        return fexe

    def find_wheel(self):
        exename = 'wheel'
        exepath = get_executable(exename)
        if not exepath:
            pip = get_executable('pip')
            cmd = pip + ' install wheel[signatures]'
            if win32:
                # self.ctx.run(cmd, echo=True)
                runners.run(cmd)
                wheel = get_executable(exename)
                # generate signing key if downloading wheel
                runners.run(wheel + ' keygen')
            else:
                raise MissingCommand("Missing twine (%s)" % cmd)
            print 'Your ~/.pypirc file should have a [pypi] section instead of a [server-login] section'
        return exepath

    def find_twine(self):
        exename = 'twine'
        exepath = get_executable(exename)
        if not exepath:
            pip = get_executable('pip')
            cmd = pip + ' install twine'
            if win32:
                # self.ctx.run(cmd, echo=True)
                runners.run(cmd)
                exepath = get_executable(exename)
            else:
                raise MissingCommand("Missing twine (%s)" % cmd)
            print 'Your ~/.pypirc file should have a [pypi] section instead of a [server-login] section'
        return exepath

    def find_uglify(self):
        exename = 'uglifyjs'
        exepath = get_executable(exename)
        if not exepath:
            npminstall = "npm install -g uglify-js --no-color"
            if win32:
                self.ctx.run(npminstall, echo=False, encoding="utf-8")
                exepath = get_executable(exename)
            else:
                raise MissingCommand("Missing uglifyjs (%s)" % npminstall)
        return exepath

    def find_browserify(self):
        exename = 'browserify'
        exepath = get_executable(exename)
        npminstall = "npm install -g browserify --no-color"
        if not exepath:
            if win32:
                #self.ctx.run(npminstall, echo=False, encoding="utf-8")
                self.ctx.run(npminstall, echo=True, encoding="utf-8")
                exepath = get_executable(exename)
            else:
                raise MissingCommand("Missing browserify (%s)" % npminstall)
        return exepath

    def find_babili(self):
        exename = 'babili'
        exepath = get_executable(exename)
        npminstall = "npm install -g babili --no-color"
        if not exepath:
            if win32:
                self.ctx.run(npminstall, echo=False, encoding="utf-8")
                exepath = get_executable(exename)
            else:
                raise MissingCommand("Missing babili (%s)" % npminstall)
        return exepath

    def find_babel(self):
        exename = 'babel'
        exepath = get_executable(exename)
        npminstall = "npm install -g babel --no-color"
        if not exepath:
            if win32:
                self.ctx.run(npminstall, echo=False, encoding="utf-8")
                exepath = get_executable(exename)
            else:
                raise MissingCommand("Missing babel (%s)" % npminstall)
        return exepath

    def find_nodejs(self):  # pragma: nocover
        """Find :program:`node`.
        """
        if sys.platform == 'win32':
            node_exe = get_executable('node')
        else:
            node_exe = get_executable('nodejs') or get_executable('node')

        if not node_exe:  # pragma: nocover
            raise MissingCommand("""
            Install Node.js using your OS package manager
            https://github.com/joyent/node/wiki/Installing-Node.js-via-package-manager
            """)
        return node_exe

    def find_npm(self):
        """Find the node package manager (:program:`npm`).
        """
        npm_exe = get_executable('npm')
        if not npm_exe:  # pragma: nocover
            raise MissingCommand("""
            Install Node.js using your OS package manager
            https://github.com/joyent/node/wiki/Installing-Node.js-via-package-manager
            """)
        return npm_exe


#: public interface to the :py:class:`Executables` class
exe = Executables()


def requires(*deps):
    """Decorator to declare global dependencies/requirements.

       Usage (``@task`` must be last)::

           @requires('nodejs', 'npm', 'lessc')
           @task
           def mytask(..)

    """
    def _wrapper(fn):
        exe.require(*deps)
        return fn
    return _wrapper




