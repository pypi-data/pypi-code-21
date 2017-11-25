from getmyipcawen.common.common import setup_logger, get_url
from getmyipcawen.getmyip import getip
import logging
import argparse

log = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")
    args = parser.parse_args()
    if args.verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    setup_logger(level)
    url = get_url()
    print(getip(url))

if __name__ == '__main__':
    main()

