from typing import List

from stuffer import apt
from stuffer import files
from stuffer.core import Group, Action


class ChromeStable(Group):
    def children(self) -> List[Action]:
        return [
            apt.KeyAdd("https://dl.google.com/linux/linux_signing_key.pub"),
            apt.SourceList("google-chrome", "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main"),
            apt.Install('google-chrome-stable'),
            # Don't recall why this is necessary, but it is. :-)
            apt.Install('libnss3-tools')
        ]


class NameServer(Group):
    """Add a Google nameserver last to resolv.conf (through resolvconf). Not to be used in Docker."""

    def children(self) -> List[Action]:
        return [
            # Make parent directories in case we are in a docker container during testing.
            files.Content("/etc/resolvconf/resolv.conf.d/tail", "nameserver 8.8.8.8\n", make_dirs=True)
        ]
