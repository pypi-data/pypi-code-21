from ievv_opensource.utils.logmixin import LogMixin
from ievv_opensource.utils.shellcommandmixin import ShellCommandMixin


class AbstractInstaller(LogMixin, ShellCommandMixin):
    """
    Base class for installers.

    Each installer defines most of their own API, the only thing they
    have in common is a reference to their
    :class:`ievv_opensource.utils.ievvbuildstatic.config.App`,
    a :obj:`~.AbstractInstaller.name` and the methods
    defined in :class:`ievv_opensource.utils.logmixin.LogMixin`
    and :class:`ievv_opensource.utils.ievvbuildstatic.shellcommand.ShellCommandMixin`.

    Plugins instantiate installers using
    :meth:`ievv_opensource.utils.ievvbuildstatic.config.App.get_installer`.
    """

    #: The name of the installer.
    name = None

    def __init__(self, app):
        """
        Parameters:
            app: The :class:`ievv_opensource.utils.ievvbuildstatic.config.App` where
                this installer object was instantiated using
                :meth:`ievv_opensource.utils.ievvbuildstatic.config.App.get_installer`.
        """
        self.app = app

    def get_logger_name(self):
        return '{}.{}'.format(self.app.get_logger_name(), self.name)

    def get_loglevel(self):
        return self.app.apps.loglevel

    def get_command_error_message(self):
        return self.app.apps.command_error_message

    def initialize(self):
        raise NotImplementedError()
