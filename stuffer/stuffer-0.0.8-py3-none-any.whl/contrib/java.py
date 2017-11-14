from stuffer import apt
from stuffer import debconf
from stuffer.core import Action


class Jdk(Action):
    def __init__(self, version):
        self.version = version
        super().__init__()

    def run(self):
        apt.AddRepository('ppa:webupd8team/java').execute()
        debconf.SetSelections('debconf', 'shared/accepted-oracle-license-v1-1', 'select', 'true').execute()
        debconf.SetSelections('debconf', 'shared/accepted-oracle-license-v1-1', 'seen', 'true').execute()
        apt.Install('oracle-java{}-installer'.format(self.version)).execute()

