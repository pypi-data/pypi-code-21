import sys


class CliPrinter(object):

    printed_something = False

    def echo(self, *args):
        if not self.printed_something:
            print()
            self.printed_something = True
        print(' ', *args)

    def final_echo(self):
        if self.printed_something:
            print()


global_printer = CliPrinter()


class CliApp(object):

    printer = global_printer

    def __init__(self):
        self.commands = []

    def command(self, command):
        self.commands.append(command)

    def call(self):
        args = sys.argv[1:]
        self.run(args)

    def run(self, args):
        if args:
            name = args.pop(0)
            command = self._find_target_command(name)
            if command:
                command.call(*args)
            else:
                self.echo('ERROR:', 'Unknown command "{}"'.format(name))
        else:
            self.print_help()
        self.printer.final_echo()

    def _find_target_command(self, name):
        for command in self.commands:
            if command.name == name:
                return command
        return None

    def print_help(self):
        self.echo('Commands:')
        self.echo()
        space_padding = max([len(command.usage) for command in self.commands]) + 2
        for command in self.commands:
            spaces = space_padding - len(command.usage)
            self.echo(command.usage, ' ' * spaces, command.description)

    def echo(self, *args):
        self.printer.echo(*args)


class CliCommand(object):

    name = None
    usage = None
    description = None
    printer = global_printer

    def call(self, *args):
        try:
            self.run(*args)
        except TypeError as e:
            message = str(e)
            message = message.replace('run()', '').strip()
            if self.usage:
                self.echo('USAGE:', self.usage)
            self.echo('ERROR:', message)

    def echo(self, *args):
        self.printer.echo(*args)

    def abort(self, *args):
        if args:
            self.printer.echo(*args)
        self.printer.final_echo()
        sys.exit(1)
