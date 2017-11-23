# coding=utf-8
import click
from distutils.version import LooseVersion
import pkg_resources

import russell
from russell.cli.auth import login, logout
from russell.cli.data import data
from russell.cli.experiment import delete, info, logs, output, status, stop, log
from russell.cli.run import run
from russell.cli.project import init, clone, clone2
from russell.client.version import VersionClient
from russell.client.service import ServiceClient
from russell.exceptions import RussellException
from russell.log import configure_logger
from russell.log import logger as russell_logger

def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    server_version = VersionClient().get_cli_version()
    current_version = pkg_resources.require("russell-cli")[0].version
    click.echo('Version: {}'.format(current_version))
    click.echo('Remote latest version: {}'.format(server_version.latest_version))
    if LooseVersion(current_version) < LooseVersion(server_version.min_version):
        raise RussellException("""
    Your version of CLI ({}) is no longer compatible with server. Run:
        pip install -U russell-cli
    to upgrade to the latest version ({})
                """.format(current_version, server_version.latest_version))
    if LooseVersion(current_version) < LooseVersion(server_version.latest_version):
        click.echo("""
    New version of CLI ({}) is now available. To upgrade run:
        pip install -U russell-cli
                """.format(server_version.latest_version))
    ctx.exit()

@click.group()
@click.option('-h', '--host', default=russell.russell_host, help='Russell server endpoint')
@click.option('-v', '--verbose', count=True, help='Turn on debug logging')
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True, help="Show version info")
def cli(host, verbose):
    """
    Russell CLI interacts with Russell server and executes your commands.
    More help is available under each command listed below.
    """
    russell.russell_host = host
    configure_logger(verbose)
    check_cli_version()
    check_server_status()


def check_cli_version():
    """
    Check if the current cli version satisfies the server requirements
    """
    server_version = VersionClient().get_cli_version()
    current_version = pkg_resources.require("russell-cli")[0].version
    if LooseVersion(current_version) < LooseVersion(server_version.min_version):
        raise RussellException("""
Your version of CLI ({}) is no longer compatible with server. Run:
    pip install -U russell-cli
to upgrade to the latest version ({})
            """.format(current_version, server_version.latest_version))
    if LooseVersion(current_version) < LooseVersion(server_version.latest_version):
        click.echo("""
New version of CLI ({}) is now available. To upgrade run:
    pip install -U russell-cli
            """.format(server_version.latest_version))


def check_server_status():
    """
    Check if russell cloud service status now
    """
    service = ServiceClient().get_service_status()
    if service.service_status <= 0:
        raise RussellException("""
            System is being maintained. Please wait until the end. 
        """)



def add_commands(cli):
    cli.add_command(data)
    cli.add_command(delete)
    cli.add_command(info)
    cli.add_command(init)
    cli.add_command(login)
    cli.add_command(logout)
    cli.add_command(logs)
    cli.add_command(output)
    cli.add_command(status)
    cli.add_command(stop)
    cli.add_command(run)
    cli.add_command(clone)



add_commands(cli)
