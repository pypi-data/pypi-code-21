
def add_commands(subparsers):
    staging_parser = subparsers.add_parser('staging')
    staging_subparsers = staging_parser.add_subparsers()

    upload_parser = staging_subparsers.add_parser('upload')
    upload_parser.add_argument("file", metavar="<file>")
    upload_parser.add_argument("urn", metadata="<urn>")
    upload_parser.set_defaults(func=foo)


def foo():
    pass
