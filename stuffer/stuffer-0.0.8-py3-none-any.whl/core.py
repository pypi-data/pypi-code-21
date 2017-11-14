import abc
import logging
import subprocess
from pathlib import Path
from typing import List, Union
from urllib.parse import urlparse

from stuffer.content import StringArg
from stuffer.utils import NaturalReprMixin, str_split


class ActionRegistry(object):
    """Singleton class to keep track of the created Actions."""

    _registry = []
    """The actions that have been registered."""

    @classmethod
    def register(cls, action):
        cls._registry.append(action)

    @classmethod
    def registered(cls):
        return list(cls._registry)


class Action(NaturalReprMixin):
    """Base class for actions to be taken.

    Subclasses should override either command() or run(). If command() is overridden, it will get logged to stdout. If
    run() is overridden, the implementation should provide some form of logging.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        ActionRegistry.register(self)
        logging.debug("Registered action: {}".format(self))

    def execute(self) -> None:
        """Execute the action, including any prerequisites."""
        logging.info("Executing {}".format(self))
        for prereq in self.prerequisites():
            prereq.run()
        self.run()

    def prerequisites(self):
        return []

    def command(self) -> Union[StringArg, List[str]]:
        """Shell command to run. Override this or run().

        Should either return a list of strings to pass to subprocess.check_output, or a string, in which case shell=True
        will be passed with subprocess.check_output..
        """
        pass

    @staticmethod
    def tmp_dir() -> Path:
        """Directory for temporary file storage, e.g. downloaded files."""
        return Path("/tmp/stuffer_tmp")

    def run(self) -> str:
        """Run the Action command(s).

        The default implementation runs the command returned by command().

        Returns
        -------
        str
            The output of the command

        Raises
        ------
        subprocess.CalledProcessError
            On execution failure.
        """
        return run_cmd(self.command())

    @staticmethod
    def _extract_net_archive(uri, destination):
        # TODO: Verify checksum
        # noinspection PyUnresolvedReferences
        archive_name = Path(urlparse(uri).path).parts[-1]
        if not destination.is_dir():
            destination.mkdir(parents=True)
        local_archive = Action.tmp_dir() / archive_name
        if not local_archive.exists():
            run_cmd(["wget", "--output-document", str(local_archive), uri])
        run_cmd(["tar", "--directory", str(destination), "-xf", str(local_archive)])


class Group(Action):
    """Group of multiple actions to be executed."""

    @abc.abstractmethod
    def children(self) -> List[Action]:
        """Returns list of child actions to execute."""
        raise NotImplementedError()

    def run(self) -> None:
        for child in self.children():
            child.execute()


def run_cmd(cmd: List[str], *args, **kwargs):
    """Run a shell command and return the output.

    Parameters
    ----------
    cmd
        List of command and arguments, passed to subprocess.check_output. If a string is passed, shell=True will
        be added to kwargs.
    args
        Extra arguments passed to subprocess.check_output
    kwargs
        Extra keyword arguments passed to subprocess.check_output

    Returns
    -------
    The output of the command

    Raises
    ------
    subprocess.CalledProcessError
        On execution failure.
    """
    joined = " ".join(str_split(cmd))
    logging.info("> %s", joined)
    try:
        output_bytes = subprocess.check_output(cmd, *args, shell=type(cmd) is str, **kwargs)
        output = output_bytes.decode(encoding="ascii", errors="ignore")
        logging.debug(output)
        return output
    except subprocess.CalledProcessError as err:
        logging.error("Command %s failed:\n%s", joined, str(err.output))
        raise
