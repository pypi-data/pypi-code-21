import click
from click import Path

import src

@click.command()
@click.argument('seed_name')
@click.option('--config', '-c', default='gardener.yml', help='Location of the config file', type=Path())
@click.option('--seed_location', '-l', default='./seeds', help='Location of the Seeds', type=Path())
@click.option('--project_name', '-n', default=None, help='The project name, used for the generation', type=str)
@click.option('--destination', '-d', default='./dist', help='The destination of the generation process', type=Path())
def generate(config, seed_location, seed_name, project_name, destination):

    project_name = project_name or seed_name
    """Generate a project from SEED template at DESTINATION"""
    cli_data = {
        'config_file_location': config,
        'seed_name': seed_name,
        'seed_location': seed_location,
        'project_name': project_name,
        'destination': destination
    }

    src.run(cli_data)


