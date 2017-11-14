from stuffer import apt
from stuffer import content
from stuffer.core import Group


class Docker(Group):
    def children(self):
        return [apt.Install(["apt-transport-https", "ca-certificates"]),
                apt.KeyRecv("hkp://p80.pool.sks-keyservers.net:80", "58118E89F3A912897C070ADBF76221572C52609D"),
                apt.Install('lsb-release'),
                apt.SourceList("docker",
                               content.OutputOf(
                                   'echo "deb https://apt.dockerproject.org/repo ubuntu-$(lsb_release -c -s) main"'))
                ]
