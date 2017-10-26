import click


@click.group()
def files():
    pass


@files.command()
def sum():
    pass


@files.command()
def cat():
    pass


@files.command()
def hadd():
    pass


@files.group()
def clears():
    """
    Quick cleaner of prefab utiles
    """


@clears.option("--name", "-n", type=str, help="Name of prefab utiles.")
def pyc():
    pass


@click.group()
def dirs():
    pass


@dirs.command()
def merge():
    pass


@dirs.command()
def sbatch():
    pass
