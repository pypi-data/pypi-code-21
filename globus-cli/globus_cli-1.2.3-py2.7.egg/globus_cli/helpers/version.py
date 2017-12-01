from globus_cli.safeio import safeprint
from globus_cli.version import get_versions


def print_version():
    """
    Print out the current version, and at least try to fetch the latest from
    PyPi to print alongside it.

    It may seem odd that this isn't in globus_cli.version , but it's done this
    way to separate concerns over printing the version from looking it up.
    """
    latest, current = get_versions()
    if latest is None:
        safeprint(('Installed Version: {0}\n'
                   'Failed to lookup latest version.')
                  .format(current))
    else:
        safeprint(
            ('Installed Version: {0}\n'
             'Latest Version:    {1}\n'
             '\n{2}').format(
                current, latest,
                'You are running the latest version of the Globus CLI'
                if current == latest else
                ('You should update your version of the Globus CLI with\n'
                 '  globus update')
                 if current < latest else
                 'You are running a preview version of the Globus CLI'
            )
        )
