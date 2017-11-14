"""
Package installation with apt commands.

Packages are installed with apt.Install. Third-party package repositories can be added with
apt.AddRepository or apt.SourceList. Repository keys are added with either apt.KeyAdd or
apt.KeyRecv.

There is no command corresponding to ``apt-get update``, since it is considered bad practice to run
and update in isolation. Instead, update is executed automatically only when necessary, i.e. for the
first apt.Install command, and in case new package repositories or repository keys have been
added. The state key apt.UPDATE_NEEDED_KEY is used to communicate to later commands whether an
update is necessary or not.

Attributes
----------

UPDATE_NEEDED_KEY : str
   Name of store variable used to signal the need to run ``apt-get update``.
"""

import os
from pathlib import Path
from typing import Optional, Union, List

from stuffer import content
from stuffer import store
from stuffer.files import write_file_atomically
from stuffer.content import StrSupplier, StringArg
from .core import Action, run_cmd


UPDATE_NEEDED_KEY = "stuffer.apt.update_needed"


def _apt_run(cmd, **kwargs):
    return run_cmd(cmd, env=dict(os.environ, DEBIAN_FRONTEND='noninteractive'), **kwargs)


class Install(Action):
    """Install a package with apt-get install.

    ``apt-get update`` will ne executed first, unless the value for apt.UPDATE_NEEDED_KEY indicates
    that update is unnecessary.

    Parameters
    ----------
    package
        Name of package. Standard ``apt-get install`` version constraints can be used, e.g. ``wget=1.17.1``.
    update
        Whether to run ``apt-get update`` first. If absent, it is automatically decided.

    """

    def __init__(self, package: Union[StringArg, List[str]], update: Optional[bool]=None):
        self.update = update
        self.packages = [package] if isinstance(package, str) else list(package)
        super(Install, self).__init__()

    def _update_needed(self) -> bool:
        if self.update is None:
            return store.get_value(UPDATE_NEEDED_KEY) != "False"
        return self.update

    def run(self) -> None:
        if self._update_needed():
            _apt_run(["apt-get", "update"])
            store.set_value(UPDATE_NEEDED_KEY, "False")
        _apt_run(["apt-get", "install", "--yes"] + self.packages)


class AddRepository(Action):
    """Add an apt repository with apt-add-repository.

    Parameters
    ----------
    name
        Name of repository.
    """

    def __init__(self, name: StringArg):
        self.name = name
        super(AddRepository, self).__init__()

    def prerequisites(self):
        return [Install("software-properties-common", update=False)]

    def run(self):
        _apt_run(["add-apt-repository", "--yes", self.name])
        store.set_value(UPDATE_NEEDED_KEY, "True")


class KeyAdd(Action):
    """Add a trusted key to apt using ``apt-key add`` method.

    Parameters
    ----------
    url
        URL of key file to download.
    """

    def __init__(self, url: StringArg):
        self.url = url
        super(KeyAdd, self).__init__()

    def prerequisites(self):
        return [Install('wget', update=False)]

    def run(self):
        _apt_run("wget {} -O - | apt-key add -".format(self.url))
        store.set_value(UPDATE_NEEDED_KEY, "True")


class KeyRecv(Action):
    """Add a trusted key to apt using apt-key --recv-keys method.

    Parameters
    ----------
    keyserver
        Host name of key server, passed as --keyserver argument.
    key
        Key hex code.
    """

    def __init__(self, keyserver: StringArg, key: StringArg):
        self.keyserver = keyserver
        self.key = key
        super(KeyRecv, self).__init__()

    def run(self):
        _apt_run(["apt-key", "adv", "--keyserver", self.keyserver, "--recv-keys", self.key])
        store.set_value(UPDATE_NEEDED_KEY, "True")


class Purge(Action):
    """Completely remove a package.

    Runs the ``apt-get purge`` command.

    Parameters
    ----------
    package
        Name of package.
    """

    def __init__(self, package: StringArg):
        self.packages = [package] if isinstance(package, str) else list(package)
        super().__init__()

    def command(self):
        return ["apt-get", "purge", "--yes"] + self.packages


class SourceList(Action):
    """Add a package repository by creating a file under /etc/apt/sources.list.d.

    Parameters
    ----------
    name
        Name of repository file, without extension
    contents
        Contents of file, e.g. ``deb https://apt.dockerproject.org/repo ubuntu-xenial main``,
        or function that returns the contents when called.
    """

    def __init__(self, name: StringArg, contents : Union[StringArg, StrSupplier]):
        self.name = name
        self.contents = content.supplier(contents)
        super(SourceList, self).__init__()

    def prerequisites(self):
        return [Install('apt-transport-https', update=False)]

    def run(self):
        write_file_atomically(Path("/etc/apt/sources.list.d").joinpath(self.name).with_suffix(".list"),
                              self.contents().rstrip() + "\n")
        store.set_value(UPDATE_NEEDED_KEY, "True")
