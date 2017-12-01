import click

from globus_cli.safeio import safeprint
from globus_cli.parsing import common_options
from globus_cli.config import get_config_obj


@click.command('remove', help='Remove a value from the Globus config file')
@common_options(no_format_option=True)
@click.argument('parameter', required=True)
def remove_command(parameter):
    """
    Executor for `globus config remove`
    """
    conf = get_config_obj()

    section = "cli"
    if '.' in parameter:
        section, parameter = parameter.split('.', 1)

    # ensure that the section exists
    if section not in conf:
        conf[section] = {}
    # remove the value for the given parameter
    del conf[section][parameter]

    # write to disk
    safeprint('Writing updated config to {}'.format(conf.filename))
    conf.write()
