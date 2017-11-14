import logging
from pathlib import Path

from stuffer import apt
from stuffer.core import Action


class IntelliJ(Action):
    def __init__(self, version, build, variant="IC", destination="/usr/local"):
        self.version = version
        self.build = build
        self.variant = variant
        self.destination = Path(destination)
        super(IntelliJ, self).__init__()

    def prerequisites(self):
        return [apt.Install(["wget"], update=False)]

    def run(self):
        tar_file_name = "idea{}-{}.tar.gz".format(self.variant, self.version)
        if not self.path():
            logging.info("Installing idea%s-%s", self.variant, self.version)
            tar_url = 'http://download.jetbrains.com/idea/{}'.format(tar_file_name)
            self._extract_net_archive(tar_url, self.destination)

    def path(self):
        matches = list(self.destination.glob("idea-{}-{}.*".format(self.variant, self.build)))
        if matches:
            return matches[-1]
        return None
