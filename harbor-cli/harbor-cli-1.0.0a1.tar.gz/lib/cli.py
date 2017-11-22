''' All CLI hooks are handled through here. '''
import click
from pyfiglet import Figlet

from lib import __version__
from lib.logger import init_logger

from lib.commands.deploy import Deploy
from lib.commands.invite import Invite
from lib.commands.register import Register

REGISTER_HELP_TEXT = 'Flag to indicate if a user is to be registered.'
DEPLOY_HELP_TEXT = 'Release type [qa, uat, dev].\
        This affects the audience that receives notice of this release.\
        Default value of "dev" is assumed'
INVITATION_HELP_TEXT = 'Role to register the user under [qa, uat, dev].\
        This affects how they receive updates regarding releases.\
        Default value of "dev" is assumed.'
INVALID_ROLE = 'Role {0} is not valid. Please use one of ["qa", "uat", "dev"] '
INVALID_DEPLOY_TYPE = 'Please use "uat", "qa" or "dev" as the deploy type'
INVALID_EMAIL = '"{0}" is not a valid email.'
NOCONFIRM_HELP = 'Don\'t ask for confirmation'

# Clear the screen.
click.clear()

# Show a ASCII art on the screen.
print(Figlet().renderText('HARBOR'))

# Initalize logger.
init_logger()


@click.version_option(__version__, message='%(version)s')
@click.group()
def cli():
    ''' CLI for the Harbor application. '''
    pass


@click.command()
@click.option('--user', is_flag=True, help=REGISTER_HELP_TEXT)
def register(user):
    ''' Register your project/user on the server. '''
    Register(user).execute()


@click.command()
@click.option('--deploy-type', help=DEPLOY_HELP_TEXT)
@click.option('--noconfirm', help=NOCONFIRM_HELP)
def deploy(deploy_type, noconfirm):
    ''' Deploy your project once it has been registered. '''
    Deploy(deploy_type).execute()


@click.command()
@click.argument('email')
@click.option('--role', help=INVITATION_HELP_TEXT)
def invite(email, role):
    ''' Invite someone to the project. '''
    Invite(email, role).execute()


cli.add_command(register)
cli.add_command(deploy)
cli.add_command(invite)
