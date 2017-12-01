import click


@click.command()
@click.option('--function', '-f', type=str, help='Function name you will use installed package')
@click.argument('name')
@click.argument('version')
def install(function, name, version):
    if version:
        version = f'=={version}'
