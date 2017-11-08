# -*- coding: utf-8 -*-
import click
from click import argument, option, types  # noqa
import contextlib
from modelhub.core import conf


@click.group()
def main():
    "Modelhub - a Model management system"
    pass


def register(name):
    def wrapper(command_cls):
        assert issubclass(command_cls, BaseCommand)
        command_cls.name = name

        @contextlib.wraps(command_cls.run)
        def command(*args, **kwargs):
            command_cls().run(*args, **kwargs)
        for arg in reversed(command_cls.add_arguments()):
            command = arg(command)
        main.add_command(click.command(command_cls.name)(command))
        return command_cls
    return wrapper


class BaseCommand():

    @staticmethod
    def echo(*args, **kwargs):
        return click.echo(*args, **kwargs)

    arguments = []

    @classmethod
    def add_arguments(cls):
        return cls.arguments

    def get_user_info(self):
        if conf.USER_NAME is None or conf.USER_EMAIL is None:
            self.echo("""You have to set user infomation on ~/.modehubrc
Example:
[user]
name = Jack Jones
email = jack@example.com
                """)
            raise ValueError
        return conf.USER_NAME, conf.USER_EMAIL
