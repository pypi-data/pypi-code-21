from termify import *
import argparse


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("lang", help="set the language of the lyrics")
    parser.add_argument("-t", "--translation", help="show the translation of the lyrics")

    return parser.parse_args()


def main():
    """Display lyrics"""
    try:
        args = get_args()
        if args.translation:
            get_lyrics(args.lang, True)
        else:
            get_lyrics(args.lang, False)

    except Exception as e:
        print(AsciiTable(
            [
                ['Sorry! An error occurred while trying to retrieve the lyrics'],
                ['Cause: ' + str(e)]
            ], 'Error').table)
