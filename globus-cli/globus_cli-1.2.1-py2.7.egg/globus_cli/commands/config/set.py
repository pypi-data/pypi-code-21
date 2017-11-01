import click

from globus_cli.safeio import safeprint
from globus_cli.parsing import common_options
from globus_cli.config import get_config_obj


@click.command('set', help='Set a value in the Globus config file')
@common_options(no_format_option=True)
@click.argument('parameter', required=True)
@click.argument('value', required=True)
def set_command(value, parameter):
    """
    Executor for `globus config set`
    """
    conf = get_config_obj()

    section = "cli"
    if '.' in parameter:
        section, parameter = parameter.split('.', 1)

    # ensure that the section exists
    if section not in conf:
        conf[section] = {}
    # set the value for the given parameter
    conf[section][parameter] = value

    # write to disk
    safeprint('Writing updated config to {}'.format(conf.filename))
    conf.write()
