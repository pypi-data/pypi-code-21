import click


@click.group()
def new():
    pass


@new.command()
@click.option('--name', '-n', type=str)
@click.option('--path', '-p', type=str, default='.')
def component(name, path):
    from . api import SnippetMaker
    SnippetMaker.component(name, path)


class CLI(click.MultiCommand):
    """
        Code maker
    """
    commands = {'new': None}

    def __init__(self):
        super(__class__, self).__init__(name='code', help=__class__.__doc__)

    def list_commands(self, ctx):
        return sorted(self.commands.keys())

    def get_command(self, ctx, name):
        if name in self.commands:
            if self.commands[name] is None:
                mapping = {
                    'new': new,
                }
                self.commands[name] = mapping.get(name)
        return self.commands.get(name)


main = CLI()
