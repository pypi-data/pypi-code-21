import sys
import argparse

from fizzgun.bin.cli_commands import CmdRunFizzgun, CmdGenerateConfig, CmdBubbles


def main(args=None):
    if sys.path[0] != '':
        sys.path.insert(0, '')

    parser = argparse.ArgumentParser(description='Fizzgun')

    subparsers = parser.add_subparsers(title='Commands', dest='command_name')

    cmd = subparsers.add_parser('run', help="Start fizzgun")
    cmd.add_argument("-c", "--config", metavar="FILE", default=None,
                     help="Fizzgun YAML configuration file")
    cmd.set_defaults(cmd_class=CmdRunFizzgun)

    cmd = subparsers.add_parser('gen-config', help="Generate sample config file")
    cmd.add_argument("-f", "--filename", metavar="FILE", default=None,
                     help="Destination file name (default: 'fizzgun.yaml')")
    cmd.add_argument("--defaults", action="store_true",
                     help="Generate config file with default settings")
    cmd.set_defaults(cmd_class=CmdGenerateConfig)

    cmd = subparsers.add_parser('bubbles', help="Show information about existing bubbles")
    cmd.add_argument("-c", "--config", metavar="FILE", default=None,
                     help="Fizzgun YAML configuration file")
    cmd.set_defaults(cmd_class=CmdBubbles)

    options = parser.parse_args(args)

    if not options.command_name:
        parser.error("No command specified.")

    options.cmd_class().run(options)


if __name__ == "__main__":
    main()
