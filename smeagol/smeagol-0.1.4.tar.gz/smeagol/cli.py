import argparse
from . import server

def run():
    parser = build_parser()
    args = parser.parse_args()
    args.func()


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose')
    parser.set_defaults(func=server.run)

    return parser

if __name__ == '__main__':
    run()
