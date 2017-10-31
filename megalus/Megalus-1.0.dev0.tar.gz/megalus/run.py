"""Ferramenta Megalus.

Para mais detalhes digite 'meg help'

Usage:
    meg help
    meg project

Options:
    --help          Mostra esta tela

"""
import re
import sys
from docopt import docopt
from buzio import console
from megalus import __version__
from megalus.projects.config import settings
from megalus.version import check_version


class Command():
    """Command class."""

    def __init__(self, settings):
        """Function: __init__.

        Summary: InsertHere
        Examples: InsertHere
        Attributes:
            @param (self):InsertHere
            @param (project):InsertHere
            @param (profile):InsertHere
        Returns: InsertHere
        """
        self.settings = settings

    def run(self, arguments):
        """Function: run.

        Summary: InsertHere
        Examples: InsertHere
        Attributes:
            @param (self):InsertHere
            @param (arguments):InsertHere
        Returns: InsertHere
        """
        self.arguments = arguments
        matches = re.finditer(r"(meg )(\w+)", __doc__)
        command = [
            m.group(2)
            for m in matches
            if self.arguments[m.group(2)]
        ][0]

        if command:
            function = getattr(self, "run_{}".format(command))
            return function()
        else:
            return False

    def run_project(self):
        """Function: project.

        Summary: InsertHere
        Examples: InsertHere
        Attributes:
            @param (self):InsertHere
        Returns: InsertHere
        """
        console.info("Rodando configuração de projeto.")
        return True


def main():
    """Function: main.

    Summary: InsertHere
    Examples: InsertHere
    Returns: InsertHere
    """
    console.box("Megalus v.{}".format(__version__))
    check_version()
    arguments = docopt(__doc__, version=__version__)

    settings.get_data()

    if not settings.has_project:
        settings.create_project()

    if settings.ready:
        command = Command(settings)
        ret = command.run(arguments)
    else:
        ret = False

    if not ret:
        print('\n')
    else:
        print("\nOperação finalizada.\n")

    sys.exit(ret)


if __name__ == "__main__":
    main()
