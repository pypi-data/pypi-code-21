"""Installing Python packages with pip."""
from stuffer.content import StringArg
from stuffer.core import Action
from stuffer import apt


class Install(Action):
    """Install a package with pip install.

    Parameters
    ----------
    package
        Name of package. Names may include version specification, e.g. "==1.2.3", which is passed on to
        ``pip install``."
    upgrade
        Whether to upgrade an already installed package, i.e. pass the ``--upgrade`` flag.
    bootstrap
        If true (default), ensure that the pip command is installed first.
    """

    def __init__(self, package: StringArg, upgrade: bool = False, bootstrap: bool = True):
        self.package = package
        self.upgrade = upgrade
        self.bootstrap = bootstrap
        super(Install, self).__init__()

    def prerequisites(self):
        return [
            apt.Install(["python3"], update=False),
            apt.Install(["python3-pip"], update=False),
            Install('pip', upgrade=True, bootstrap=False)
        ] if self.bootstrap else []

    def command(self):
        return "pip3 install{} '{}'".format(" --upgrade" if self.upgrade else "", self.package)
