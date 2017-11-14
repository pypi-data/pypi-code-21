from typing import List

from stuffer import apt
from stuffer import debconf
from stuffer import system
from stuffer import user
from stuffer.core import Group, Action


class Wireshark(Group):
    def children(self) -> List[Action]:
        return [
            debconf.SetSelections('debconf', 'wireshark-common/install-setuid', 'select', 'true'),
            apt.Install('wireshark'),
            user.AddToGroup(system.real_user(), "wireshark")
        ]
