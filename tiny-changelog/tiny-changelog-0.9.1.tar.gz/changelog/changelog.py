import argparse
from datetime import datetime

from printers import MarkdownPrinter
from feeds import GithubFeed


def date_validator(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError('Not a valid date: {}'.format(s))


def parse_args():
    parser = argparse.ArgumentParser(
        description='Generate CHANGELOG file.'
    )
    parser.add_argument(
        '-t', '--token',
        type=str,
        help='Github token'
    )
    parser.add_argument(
        '-p', '--project',
        type=str,
        required=True,
        help='Github project (<owner>/<repo>)'
    )
    parser.add_argument(
        '-s', '--start-date',
        help='List entries starting as early as YYYY-MM-DD',
        default='1970-01-01',
        type=date_validator
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file, defaults to CHANGELOG.md',
        default='CHANGELOG.md'
    )
    parser.add_argument(
        '--with-unreleased',
        default=False,
        action='store_true',
        help='Include unreleased merged pull requests'
    )

    return parser.parse_args()


def main():
    args = parse_args()
    timeline = GithubFeed(args.project, args.token).fetch(args.start_date)

    printer = MarkdownPrinter(timeline, with_unreleased=args.with_unreleased)
    printer.print_to_file(args.output)


if __name__ == '__main__':
    main()
