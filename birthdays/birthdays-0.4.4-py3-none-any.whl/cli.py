# -*- coding: utf-8 -*-
import os
import click
from . import app

app = app.App()


@click.group()
@click.version_option()
def cli():
    """Load birthdays from a textfile, sort them and return upcoming ones.
    Example line for the textfile: '03 10 1967 John Smith'.
    """
    pass


@cli.command()
@click.argument('textfile', type=click.File('r+'))
@click.option('--sort', '-s', default='month', type=click.Choice(app.sort_keys))
def sort(textfile, sort):
    """Sort a given file by forename, surname, year, day or month.
    By default, if no sorting-flag is given, the list is sorted by month.
    """
    if app.file_is_consistent(textfile):
        # convert rows to lists containing columns as strings
        lines = app.strings_to_lists(textfile)
        lines_sorted = app.sort_lines(lines, sort)
        click.echo('Checking for file changes...')
        if lines == lines_sorted:
            click.echo('Nothing changed. No sorting needed.')
        else:
            click.echo('Changes detected.')
            # create output conform to the txt file
            lists_to_strings = [' '.join(line) for line in lines_sorted]
            strings_to_txt = os.linesep.join(lists_to_strings)
            # overwrite content in the same file
            textfile.seek(0)
            textfile.truncate()
            textfile.write(strings_to_txt)
            textfile.close()
            click.echo('Lines were sorted and written to file: ')
            click.echo(textfile.name)
    else:
        click.echo('file is NOT consistent.')


@cli.command()
@click.argument('textfile', type=click.File('rb'))
def upcoming(textfile):
    """Return upcoming birthday(s).
    """
    lines = app.strings_to_lists(textfile)
    click.echo(app.upcoming(lines))
