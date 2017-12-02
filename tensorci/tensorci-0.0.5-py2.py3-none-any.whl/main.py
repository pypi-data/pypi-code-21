import click
from commands import all_cmds

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
  pass


# Add all commands to the CLI
[cli.add_command(cmd) for cmd in all_cmds]