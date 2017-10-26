import click


@click.command()
@click.option('--name', '-n', type=str, help='Name of script to run.')
def shell(name):
    import subprocess
    from ..service import get_script
    if name is None:
        raise TypeError("Name of shell script can not be None.")
    path_file = get_script(name)
    subprocess.run(path_file.abs)
