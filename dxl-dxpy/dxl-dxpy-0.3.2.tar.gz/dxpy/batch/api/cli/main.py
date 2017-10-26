import click


class CLI(click.MultiCommand):
    commands = {'files': None, 'dirs': None}

    def __init__(self):
        super(__class__, self).__init__(name='batch', help=__class__.__doc__)

    def list_commands(self, ctx):
        return sorted(self.commands.keys())

    def get_command(self, ctx, name):
        from . import clicks
        if name in self.commands and self.commands[name] is None:
            self.commands[name] = getattr(clicks, name)
        return self.commands.get(name)


batch = CLI()
