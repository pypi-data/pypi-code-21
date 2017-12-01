import copy
import click

from globus_cli.safeio import safeprint


_command_length = 16


@click.command('list-commands', short_help='List all CLI Commands',
               help=('List all Globus CLI Commands with short help output. '
                     'For full command help, run the command with the '
                     '`--help` flag'))
def list_commands():
    def _print_cmd(command):
        # print commands with short_help
        indent = 4
        min_space = 2

        # if the output would be pinched too close together, or if the command
        # name would overflow, use two separate lines
        if len(command.name) > _command_length - min_space:
            safeprint(' '*indent + command.name)
            safeprint(' '*(indent + _command_length) + command.short_help)
        # otherwise, it's all cool to cram into one line, just ljust command
        # names so that they form a nice column
        else:
            safeprint(' '*indent + '{}{}'.format(
                command.name.ljust(_command_length), command.short_help))

    def _print_cmd_group(command, parent_names):
        parents = ' '.join(parent_names)
        if parents:
            parents = parents + ' '
        safeprint('\n=== {}{} ===\n'.format(parents, command.name))

    def _recursive_list_commands(command, parent_names=None):
        if parent_names is None:
            parent_names = []

        # names of parent commands, including this one, for passthrough to
        # recursive calls
        new_parent_names = copy.copy(parent_names) + [command.name]

        # group-style commands are printed as headers
        if isinstance(command, click.MultiCommand):
            _print_cmd_group(command, parent_names)

            # get the set of subcommands and recursively print all of them
            group_cmds = [v for v in command.commands.values()
                          if isinstance(v, click.MultiCommand)]
            func_cmds = [v for v in command.commands.values()
                         if v not in group_cmds]
            # we want to print them all, but func commands first
            for cmd in (func_cmds + group_cmds):
                _recursive_list_commands(cmd, parent_names=new_parent_names)

        # individual commands are printed solo
        else:
            _print_cmd(command)

    # get the root context (the click context for the entire CLI tree)
    root_ctx = click.get_current_context().find_root()

    _recursive_list_commands(root_ctx.command)
    # get an extra newline at the end
    safeprint('')
