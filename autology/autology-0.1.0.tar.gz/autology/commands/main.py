import argparse

from pkg_resources import iter_entry_points

from autology import topics
from autology.configuration import load_configuration_file as _load_configuration_file


def _build_arguments():
    """Load sub-commands defined in setup.py and allow them to build their arguments."""
    parser = argparse.ArgumentParser(description='Execute autology root command')
    parser.add_argument('--config', '-c', action='store', default='config.yaml',)

    # Process all of the sub-commands that have been registered
    subparsers = parser.add_subparsers(help='sub-command help')
    for ep in iter_entry_points(group='autology_commands'):
        ep.load()(subparsers)

    return parser


def _load_plugins():
    """Load plugins that are defined in setup.py"""
    for ep in iter_entry_points(group='autology_plugins'):
        ep.load()()


def main():
    parser = _build_arguments()
    args = parser.parse_args()

    # Load the plugins and allow them to set default properties in the configuration data object.
    _load_plugins()

    # Override the default values in configuration with the values from settings file.
    _load_configuration_file(args.config)

    # Initialize all of the plugins in the architecture now that the settings have been loaded
    topics.Application.INITIALIZE.publish()

    # Execute the sub-command requested. (as per the argparse documentation)
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

    topics.Application.FINALIZE.publish()


if __name__ == '__main__':
    main()
