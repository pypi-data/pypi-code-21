import click

import russell
from russell.log import configure_logger
from russell.main import check_cli_version, add_commands


@click.group()
@click.option('-v', '--verbose', count=True, help='Turn on debug logging')
def cli(verbose):
    """
    Russell CLI interacts with Russell server and executes your commands.
    More help is available under each command listed below.
    """
    russell.russell_host = "http://localhost:5000"
    russell.russell_web_host = "http://test.russellcloud.com"
    # russell.russell_proxy_host = "http://www.russellcloud.cn:8000"
    configure_logger(verbose)
    check_cli_version()

add_commands(cli)
