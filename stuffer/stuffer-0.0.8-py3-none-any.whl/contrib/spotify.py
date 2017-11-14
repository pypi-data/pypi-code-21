from typing import List

from stuffer.core import Group, Action

from stuffer import apt


class SpotifyClient(Group):
    def children(self) -> List[Action]:
        return [
            apt.KeyRecv("hkp://keyserver.ubuntu.com:80", "0DF731E45CE24F27EEEB1450EFDC8610341D9410"),
            apt.SourceList("spotify", "deb http://repository.spotify.com stable non-free"),
            apt.Install("spotify-client")
        ]
