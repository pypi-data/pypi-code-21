from typing import List

from stuffer import apt
from stuffer.core import Group, Action


class DropboxClient(Group):
    def children(self) -> List[Action]:
        return [
            apt.KeyRecv('pgp.mit.edu', '5044912E'),
            apt.SourceList('dropbox', "deb http://linux.dropbox.com/ubuntu/ xenial main"),
            apt.Install('python-gpgme'),  # For verification of proprietary daemon package.
            apt.Install('dropbox'),
        ]
