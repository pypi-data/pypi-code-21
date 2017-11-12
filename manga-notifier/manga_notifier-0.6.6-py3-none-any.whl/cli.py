# -*- coding: utf-8 -*-

import os
import difflib
import time

import click

from .storage import Favorite
from .mangastream import verify_release, all_manga
from .meow import Meow


def notify(releases):

    for release in releases:
        message = "Chapter {0} is OUT".format(release[1])
        Meow.meow(message,
                  title=release[0],
                  open=release[3],
                  timeout='3')
        time.sleep(3)


def to_json(releases):

    new = dict()
    for release in releases:
        new[release[0]] = int(release[1])

    return new

################
# CLI Commands #
################


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
pass_favorite = click.make_pass_decorator(Favorite, ensure=True)


@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@pass_favorite
def cli(favorite):

    ctx = click.get_current_context()
    if ctx.invoked_subcommand is None:
        if not favorite.empty:
            releases = verify_release(favorite.json)
            if any(releases):
                if DOWNLOAD_OPTION:
                    notify_download(releases)
                else:
                    notify(releases)
                favorite.update(to_json(releases))
        else:
            error_msg = "No favorites saved."
            error_msg += "\n\nUse : manga-notifier add 'manga' 'chapter'"
            click.echo(error_msg)


@click.command(help="Adding manga to your favorites")
@click.argument('name', type=click.STRING)
@click.argument('last_chapter', type=click.INT)
@pass_favorite
def add(favorite, name, last_chapter):

    database = all_manga()
    if name not in database:
        error_msg = "The manga [{}] did not exist".format(name)
        matches = difflib.get_close_matches(name, database, 3)
        error_msg += '\n\nDid you mean one of these?'
        error_msg += '\n    %s' % '\n    '.join(matches)
        click.echo(error_msg)
        exit()

    click.echo("Adding name=[{}] last_chapter=[{}]".format(name, last_chapter))
    favorite.add(name, last_chapter)


@click.command(help="Deleting manga from your favorites")
@click.argument('name', type=click.STRING)
@pass_favorite
def delete(favorite, name):

    if not favorite.empty:
        if name in favorite.json.keys():
            click.echo("Deleting name=[{}]".format(name))
            favorite.delete(name)
        else:
            error_msg = "[{}] is not in your favorites.".format(name)
            error_msg += "\n\nTo see your favorites: manga-notifier liste"
            click.echo(error_msg)
    else:
        error_msg = "There is no favorites to delete"
        click.echo(error_msg)


@click.command(help="Display your favorites")
@pass_favorite
def liste(favorite):

    favorites = favorite.json

    for k, v in favorites.items():
        click.echo('{} : {}'.format(k, v))


@click.command(help="Download the last chapter of the choosen manga")
@pass_favorite
def download(favorite):
    pass


# Generate click commands
cli.add_command(add)
cli.add_command(delete)
cli.add_command(liste)
cli.add_command(download)


if __name__ == '__main__':
    cli()
