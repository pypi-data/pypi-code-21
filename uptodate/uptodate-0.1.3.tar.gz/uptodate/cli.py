import click

from uptodate.core import UpToDate


@click.command()
@click.argument('file_paths', nargs=-1, type=click.Path(exists=True))
def up_to_date(file_paths):
    """Scan requirements.txt file for dependences which are not up to date"""
    if len(file_paths) > 1:
        click.secho('To many arguments', fg='red')
        return

    file_path = None
    if len(file_paths) == 1:
        file_path = file_paths[0]

    uptodate = UpToDate(file_path)
    uptodate.check()


if __name__ == '__main__':
    up_to_date()
