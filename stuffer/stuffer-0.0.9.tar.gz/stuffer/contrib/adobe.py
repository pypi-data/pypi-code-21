from typing import List

from stuffer.core import Group, Action

from stuffer import apt


class SpotifyClient(Group):
    def children(self) -> List[Action]:
        return [
            apt.SourceList("partner", "deb http://archive.canonical.com/ubuntu xenial partner"),
            apt.Install("spotify-client")
        ]
