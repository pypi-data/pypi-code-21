# -*- coding: utf-8 -*-

import os
import difflib
import time

import click

from .storage import Storage
from .mangastream import check_release, get_all_manga
from .meow import Meow

pass_storage = click.make_pass_decorator(Storage, ensure=True)

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

DOWNLOAD_OPTION = bool(os.environ.get('MANGA_NOTIFIER_DOWNLOAD'))


def notify(releases):

    for release in releases:
        message = "Chapter {0} is OUT".format(release[1])
        Meow.meow(message,
                  title=release[0],
                  open=release[3],
                  timeout='3')
        time.sleep(3)


def notify_download(releases):

    for release in releases:
        message = "Chapter {0} is OUT".format(release[1])
        r = Meow.meow(message,
                      title=release[0],
                      actions='Yes',
                      timeout='3')

        if r['activationType'] == "actionClicked":
            if r['activationValue'].lower() == 'yes':
                print('Downloading')


def to_json(releases):

    new = dict()
    for release in releases:
        new[release[0]] = int(release[1])

    return new


@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@pass_storage
def cli(storage):

    ctx = click.get_current_context()
    if ctx.invoked_subcommand is None:
        print(DOWNLOAD_OPTION)
        if any(storage.config):
            releases = check_release(storage.config)
            if any(releases):
                if DOWNLOAD_OPTION:
                    notify_download(releases)
                else:
                    notify(releases)
                storage.update(to_json(releases))
        else:
            error_msg = "No favorites saved."
            error_msg += "\n\nUse : manga-notifier add 'manga' 'chapter'"
            click.echo(error_msg)


@click.command(help="Adding manga to your favorites")
@click.argument('name', type=click.STRING)
@click.argument('last_chapter', type=click.INT)
@pass_storage
def add(storage, name, last_chapter):

    database = get_all_manga()
    if name not in database:
        error_msg = "The manga [{}] did not exist".format(name)
        matches = difflib.get_close_matches(name, database, 3)
        error_msg += '\n\nDid you mean one of these?\n    %s' % '\n    '.join(matches)
        click.echo(error_msg)
        exit()

    click.echo("Adding name=[{}] last_chapter=[{}]".format(name, last_chapter))
    storage.add(name, last_chapter)


@click.command(help="Deleting manga from your favorites")
@click.argument('name', type=click.STRING)
@pass_storage
def delete(storage, name):

    if any(storage.config):
        if name in storage.config.keys():
            click.echo("Deleting name=[{}]".format(name))
            storage.delete(name)
        else:
            error_msg = "[{}] is not in your favorites.".format(name)
            error_msg += "\n\nTo see your favorites: manga-notifier liste"
            click.echo(error_msg)


@click.command(help="Display your favorites")
@pass_storage
def liste(storage):

    favorites = storage.config

    for k, v in favorites.items():
        click.echo('{} : {}'.format(k, v))


# Generate click commands
cli.add_command(add)
cli.add_command(delete)
cli.add_command(liste)

if __name__ == '__main__':
    cli()
