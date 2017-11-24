import click
from click import Path

from pathlib import Path as PathLib

from src.core import add, generate

@click.group()
@click.option('--gardener_rc', '-g', default=None, help='Location of the global Gardener Folder', type=Path())
@click.pass_context
def cli(ctx, gardener_rc):
    if not gardener_rc:
        gardener_rc = Path(PathLib.home(), '.gardener')
    ctx.obj['gardener_rc'] = gardener_rc
    ctx.obj['gardener_rc_seed_location'] = Path(ctx.obj['gardener_rc'], 'seeds')


@cli.command()
@click.argument('to_copy', type=Path(), default=PathLib('.'))
@click.pass_context
def add(ctx, to_copy):
    cli_data = {
        'current_path': to_copy,
        'seed_location': ctx['gardener_rc_seed_location']
    }

    add(cli_data)




@cli.command()
@click.argument('seed_name')
@click.option('--config', '-c', default='gardener.yml', help='Location of the config file', type=Path())
@click.option('--seed_location', '-l', default=None, help='Location of the Seeds', type=Path())
@click.option('--project_name', '-n', default=None, help='The project name, used for the generation', type=str)
@click.option('--destination', '-d', default='./dist', help='The destination of the generation process', type=Path())
def generate(config, seed_location, seed_name, project_name, destination):

    project_name = project_name or seed_name
    """Generate a project from SEED template at DESTINATION"""
    cli_data = {
        'config_file_location': config,
        'seed_name': seed_name,
        'seed_location': seed_location, # or ctx.obj['gardener_rc_seed_location'],
        'project_name': project_name,
        'destination': destination
    }

    result = {}
    # Remove Empty values
    for key, value in cli_data.items():
        if value:
            result[key] = value

    generate(result)


