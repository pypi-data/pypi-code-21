'''Submit a certificate chain to a Certificate Transparency log (CT-log);
received SCTs will be validated.
'''

import argparse
import logging

from utlz import flo, first_paragraph

from ctutlz.utils.logger import setup_logging, VERBOSE


def create_parser():
    parser = argparse.ArgumentParser(description=first_paragraph(__doc__))
    parser.add_argument('url',
                        nargs='+',
                        help='CT-log url '
                        '(example: `ct.googleapis.com/pilot`; cf. '
                        'https://www.certificate-transparency.org/known-logs)')

    meg = parser.add_mutually_exclusive_group()
    meg.add_argument('--short',
                     dest='loglevel',
                     action='store_const',
                     const=logging.INFO,
                     default=VERBOSE,  # default loglevel if nothing set
                     help='show short result and warnings/errors only')
    meg.add_argument('--debug',
                     dest='loglevel',
                     action='store_const',
                     const=logging.DEBUG,
                     help='show more for diagnostic purposes')

    req = parser.add_argument_group("exactly-one args "
                                    "(check the 'usage' above)")
    meg = req.add_mutually_exclusive_group(required=True)
    meg.add_argument('--chain',
                     metavar='<file>',
                     help='chain file with PEM encoded certificates '
                          '(end entity cert first; '
                          'with or without root ca cert)')
    meg.add_argument('--certs',
                     nargs='+',
                     metavar='<file>',
                     help='DER or PEM encoded certificates '
                          'which build the chain '
                          '(ee cert first; with or without root ca cert)')
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    logger = setup_logging(args.loglevel)
    logger.debug(args)

    for log_url in args.url:
        print(log_url)
        # TODO DEVEL


if __name__ == '__main__':
    main()
