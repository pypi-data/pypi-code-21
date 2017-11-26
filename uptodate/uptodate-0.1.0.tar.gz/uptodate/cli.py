import click

from core import UpToDate


@click.command()
@click.argument('file_path', nargs=-1, type=click.Path(exists=True))
def up_to_date(file_path):
    """Scan requirements.txt file for dependences which are not up to date"""
    uptodate = UpToDate(file_path[0])
    uptodate.check()


if __name__ == '__main__':
    up_to_date()
