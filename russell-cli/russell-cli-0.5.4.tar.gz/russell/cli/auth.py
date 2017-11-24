import click
import webbrowser

import russell
from russell.client.auth import AuthClient
from russell.manager.auth_config import AuthConfigManager
from russell.model.access_token import AccessToken
from russell.log import logger as russell_logger
from russell.client.common import get_basic_token

@click.command()
@click.option('--token', is_flag=True, default=False, help='Just enter token')
def login(token):
    """
    Log into Russell via Auth0.
    """
    if not token:
        cli_info_url = russell.russell_web_host + "/welcome"
        click.confirm('Authentication token page will now open in your browser. Continue?', abort=True, default=True)
        webbrowser.open(cli_info_url)
        token = str(click.prompt('Please copy and paste the token here', type=str, hide_input=True))

    if not token:
        russell_logger.info("Empty token received. Make sure your shell is handling the token appropriately.")
        russell_logger.info("See FAQ for help: http://docs.russellcloud.cn/")
        return

    access_code = get_basic_token(token)

    user = AuthClient().get_user(access_code)
    access_token = AccessToken(username=user.username,
                               token=access_code)
    AuthConfigManager.set_access_token(access_token)
    russell_logger.info("Login Successful as " + user.username)


@click.command()
def logout():
    """
    Logout of Russell.
    """
    AuthConfigManager.purge_access_token()
