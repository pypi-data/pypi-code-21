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


@files.command()
@click.argument('source', nargs=1, type=str)
@click.argument('target', nargs=1, type=str)
@click.argument('filenames', nargs=-1, type=str)
@click.option('-d', '--depth', type=int, default=0)
@click.option('-v', '--verbose', is_flag=True)
def fetch(source, target, filenames, depth, verbose):
    from ...api import files_in_directories
    from fs.osfs import OSFS
    from fs.copy import copy_file
    from fs.path import dirname
    with OSFS(source) as sor:
        with OSFS(target) as tar:
            files = files_in_directories(sor, ['*'], filenames, depth)
            for f in files:
                if not tar.exists(dirname(f)):
                    tar.makedirs(dirname(f))
                copy_file(sor, f, tar, f)
                if verbose:
                    click.echo('[COPY] {} => {}.'.format(sor.getsyspath(f),
                                                         tar.getsyspath(f)))


@files.group()
def clears():
    """
    Quick cleaner of prefab utiles
    """


# @clears.option("--name", "-n", type=str, help="Name of prefab utiles.")
# def pyc():
#     pass


@click.group()
def dirs():
    pass


@dirs.command()
def merge():
    pass


@dirs.command()
def sbatch():
    pass
