import click

from globus_cli.parsing import common_options
from globus_cli.helpers import print_version


@click.command('version', help='Show the version and exit')
@common_options(no_format_option=True, no_map_http_status_option=True)
def version_command():
    """
    Executor for `globus version`
    """
    print_version()
