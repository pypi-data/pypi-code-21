import click
from click import Path

from pathlib import Path as PathLib

import src.core

@click.group()
def cli():
    pass

@cli.command('add')
@click.argument('to_copy', type=Path(), default='.')
@click.option('--gardener_rc', '-g', default=None, help='Location of the global Gardener Folder', type=Path())
@click.option('--force', '-f', default=False, help='Override the seed folder if it exists yet', is_flag=True)
def add( to_copy, gardener_rc, force):
    obj = {}
    if not gardener_rc:
        gardener_rc = PathLib(PathLib.home(), '.gardener')
    obj['gardener_rc'] = gardener_rc
    obj['gardener_rc_seed_location'] = PathLib(obj['gardener_rc'], 'seeds')


    cli_data = {
        'current_path': PathLib(to_copy),
        'seed_location': obj['gardener_rc_seed_location'],
        'override': force or False
    }

    src.core.add(cli_data)




@cli.command('generate')
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

    src.core.generate(result)


