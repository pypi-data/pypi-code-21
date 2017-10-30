import argparse
import sys
from getpass import getpass

from playlist_kreator.common import read_artists
from playlist_kreator import gmusic
from playlist_kreator import VERSION


def main(arguments):
    parser = argparse.ArgumentParser(
        prog='playlist-kreator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            'Create easily playlists. It only supports Google Music for now.\n'
            '\n'
            'Version: {}\n'
        ).format(VERSION),
    )
    subparsers = parser.add_subparsers(dest='command')

    artists_parser = subparsers.add_parser(
        'artists',
        help="Create a playlist based on a list of artists, using their top songs",
    )
    artists_parser.add_argument('artists_file', help='file with list of artists')
    artists_parser.add_argument('playlist_name', help='name of the playlist')
    artists_parser.add_argument(
        '--max-songs-per-artist',
        default=2,
        type=int,
        help='max number of songs per artist',
    )
    artists_parser.add_argument(
        '--email',
        help='optional email, if not set you will be asked in the prompt',
    )

    subparsers.add_parser('version', help="Print playlist-kreator Version")

    args = parser.parse_args(arguments)

    if args.command == 'version':
        print(VERSION)
    elif args.command == 'artists':
        artists_command(args)
    else:
        parser.print_help()


def artists_command(args):
    artists = read_artists(args.artists_file)
    print("Artists to look for: {}\n".format(artists))

    email, password = get_email_password(args)

    gmusic.create_playlist(
        args.playlist_name,
        artists,
        email,
        password,
        max_top_tracks=args.max_songs_per_artist,
    )


def get_email_password(args):
    print("It will need an email and an application password for Google Music")
    print("You can set it up here: https://myaccount.google.com/apppasswords\n")

    email = args.email
    if email:
        print("Email: {}".format(email))
    else:
        email = input("Email:")

    password = getpass("Password:")
    print()

    return email, password


if __name__ == '__main__':
    main(sys.argv[1:])
