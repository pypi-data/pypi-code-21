from .select_command import SelectCommand
from .list_area_command import ListAreaCommand
from .list_areas_command import ListAreasCommand
from .upload_command import UploadCommand


def add_commands(subparsers):
    staging_parser = subparsers.add_parser('upload')
    staging_subparsers = staging_parser.add_subparsers()

    help_parser = staging_subparsers.add_parser('help',
                                                description="Display list of upload commands.")
    help_parser.set_defaults(func=_help)

    SelectCommand.add_parser(staging_subparsers)
    ListAreasCommand.add_parser(staging_subparsers)
    UploadCommand.add_parser(staging_subparsers)
    ListAreaCommand.add_parser(staging_subparsers)


def _help(args):
    print("""
hca upload commands:

    help     print this message
    select   select a upload area to use
    areas    list upload areas we know about
    upload   upload a file to the currently selected upload area
    list     list the contents of the currently selected upload area

Use "hca upload <command> -h" to get detailed command help.
""")
