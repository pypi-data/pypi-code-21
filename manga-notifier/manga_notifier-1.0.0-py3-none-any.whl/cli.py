# -*- coding: utf-8 -*-

import sys
import difflib
import time
from collections import OrderedDict

import click

from .storage import Favorite
from .mangastream import (
    verify_release, all_manga, MANGASTREAM_URL, MANGA_EXCEPTIONS
)
from .meow import Meow
from .download import downloader


def notify(releases):
    """ Notify if there are new chapters

        Parameters
        ----------
        releases: list
            new released chapters

        Returns
        -------
        None
            nothing to return
        """
    for release in releases:
        message = "Chapter {0} is OUT".format(release[1])
        Meow.meow(message,
                  title=release[0],
                  open="{0}{1}".format(MANGASTREAM_URL, release[3]),
                  timeout='3')
        time.sleep(3)


def to_json(releases):
    """ Transform list of releases -> dict

    Parameters
    ----------
    releases: list
        new released chapters

    Returns
    -------
    dict
        a dict of releases
    """

    new = dict()
    for release in releases:
        new[release[0]] = OrderedDict({
            'chapter': int(release[1]),
            'url': "{0}".format(release[3])
        })

    return new


def download_chapter(name, chapter, url):
    """Download a chapter

    Parameters
    ----------
    name: str
        chapter's name
    chapter: str
        chapter's number
    url: str
        chapter's url

    Returns
    -------
    None
        nothing to return
    """

    print("Downloading chapter {1} of {0}".format(name, chapter))
    downloader.download(progress=True,
                        manga=name,
                        chapter=chapter,
                        url=url)


def download_all(favorites):
    """Download all your favorites's last chapter

    Parameters
    ----------
    facorites: dict
        a dict of your favorites

    Returns
    -------
    None
        nothing to return
    """
    for name, v in favorites.items():
        chapter = v['chapter']
        url = "{0}{1}".format(MANGASTREAM_URL, v['url'])
        download_chapter(name, chapter, url)


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
                notify(releases)
                favorite.update(to_json(releases))
        else:
            error_msg = "No favorites saved."
            error_msg += "\n\nUse : manga-notifier add 'manga' 'chapter'"
            click.echo(error_msg)


@click.command(help="Adding manga to your favorites")
@click.argument('name', type=click.STRING)
@pass_favorite
def add(favorite, name):

    series = all_manga()

    if name in MANGA_EXCEPTIONS.keys():
        name = MANGA_EXCEPTIONS[name]
    elif name in favorite.json.keys():
        click.echo("{0} already added".format(name))
        exit()
    elif name not in series.keys():
        error_msg = "The manga [{}] did not exist".format(name)
        matches = difflib.get_close_matches(name, series, 3)
        error_msg += '\n\nDid you mean one of these?'
        error_msg += '\n    %s' % '\n    '.join(matches)
        click.echo(error_msg)
        exit()

    message = "Adding New Favorite"
    message += "\n=> Name: '{0}'".format(name)
    message += "\n=> Chapter: '{0}'".format(series[name]['chapter'])
    click.echo(message)
    favorite.add(name, series[name]['chapter'], series[name]['url'])


@click.command(help="Deleting manga from your favorites")
@click.argument('name', type=click.STRING)
@pass_favorite
def delete(favorite, name):

    if not favorite.empty:
        if name in favorite.json.keys():
            message = "Deleting Favorite"
            message += "\n=> Name: '{0}'".format(name)
            click.echo(message)
            favorite.delete(name)
        else:
            error_msg = "'{0}'' is not in your favorites.".format(name)
            error_msg += "\n\nTo see your favorites: manga-notifier liste"
            click.echo(error_msg)
    else:
        error_msg = "There is no favorites to delete"
        click.echo(error_msg)


@click.command(help="Display your favorites")
@pass_favorite
def liste(favorite):

    if not favorite.empty:
        favorites = favorite.json

        click.echo("{:<24} {:<4}".format('Manga', 'Chapter'))
        for k, v in favorites.items():
            click.echo("{:<24} {:<4}".format(k, v['chapter']))
    else:
        error_msg = "There is no favorites to display"
        click.echo(error_msg)


@click.command(help="Download the last chapter of the choosen manga")
@click.argument('name', default=False, nargs=1, type=click.STRING)
@click.option('--all', '-a', is_flag=True, default=False)
@pass_favorite
def download(favorite, name, all):

    if not favorite.empty:

        favorites = favorite.json

        if all is True:
            download_all(favorites)
            sys.exit(0)

        if name in favorite.json.keys():
            chapter = favorites[name]['chapter']
            url = "{0}{1}".format(MANGASTREAM_URL, favorites[name]['url'])
            download_chapter(name, chapter, url)
        else:
            error_msg = "'{0}'' is not in your favorites.".format(name)
            error_msg += "\n\nTo see your favorites: manga-notifier liste"
            click.echo(error_msg)
    else:
        error_msg = "There is no favorites to download"
        click.echo(error_msg)


# Generate click commands
cli.add_command(add)
cli.add_command(delete)
cli.add_command(liste)
cli.add_command(download)


if __name__ == '__main__':
    cli()
