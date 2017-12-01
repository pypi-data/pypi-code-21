'''Retrieve an entry from a Certificate Transparency Log (ct-log),
cf. https://tools.ietf.org/html/rfc6962#section-4.6
'''

import argparse
import logging
import socket
import ssl
from pprint import pprint

import certifi
import requests
import OpenSSL.crypto
from hexdump import hexdump
from OpenSSL._util import lib as cryptolib
from utlz import flo, first_paragraph

from ctutlz import rfc6962
from ctutlz.sct.verification import verify_signature
from ctutlz.utils.encoding import decode_from_b64
from ctutlz.utils.logger import setup_logging
from ctutlz.utils.string import string_with_prefix, string_without_prefix


def create_parser():
    parser = argparse.ArgumentParser(description=first_paragraph(__doc__))
    meg = parser.add_mutually_exclusive_group()
    meg.add_argument('--short',
                     dest='loglevel',
                     action='store_const',
                     const=logging.WARNING,
                     default=logging.INFO,  # default loglevel if nothing set
                     help='show short result and warnings/errors only')
    meg.add_argument('--debug',
                     dest='loglevel',
                     action='store_const',
                     const=logging.DEBUG,
                     help='show more for diagnostic purposes')

    req = parser.add_argument_group('required arguments')
    req.add_argument('--log',
                     metavar='<url>',
                     required=True,
                     help='ct-log to retrieve '
                          '(example: `ct.googleapis.com/pilot`; cf. '
                          'https://www.certificate-transparency.org/'
                          'known-logs)')
    req.add_argument('--entry',
                     metavar='<dec>',
                     required=True,
                     help='zero-based decimal index of the log entry '
                          'to retrieve')
    req.add_argument('--signature',
                     metavar='<b64>',
                     required=True,
                     help='SCT signature, base-64 encoded')
    return parser


def get_peercert_pem(url):
    peercert_pem = None

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssl_sock = ssl.wrap_socket(sock,
                               cert_reqs=ssl.CERT_OPTIONAL,
                               ca_certs=certifi.where())
    ssl_sock.settimeout(30)
    try:
        ssl_sock.connect((url, 443))

        peercert_der = ssl_sock.getpeercert(binary_form=True)
        peercert_pem = ssl.DER_cert_to_PEM_cert(peercert_der)
    finally:
        ssl_sock.close()

    return peercert_pem


# https://stackoverflow.com/a/30929459
def pkey2pem(pkey):
    bio = OpenSSL.crypto._new_mem_buf()
    cryptolib.PEM_write_bio_PUBKEY(bio, pkey._pkey)
    return OpenSSL.crypto._bio_to_string(bio)


def get_pubkey_pem(url):
    '''Return pubkey from url's peercert PEM encoded as bytestring.'''
    peercert_pem = get_peercert_pem(url)
    x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM,
                                           peercert_pem)
    pkey = x509.get_pubkey()
    pubkey_pem = pkey2pem(pkey)
    return pubkey_pem


def get_entry(index, ctlog_url, signature_b64):
    url = string_with_prefix('https://', ctlog_url) + '/ct/v1/get-entries'
    inp = rfc6962.GetEntriesInput(start=index, end=index)
    req = requests.get(url, params=inp._asdict())
    if req.ok:
        print('--')
        # from pprint import pprint
        # pprint(req.json())
        # print(len(req.json()))
        response = rfc6962.GetEntriesResponse(json_dict=req.json())
        # pprint(response.json_dict)
        print('--')
        leaf_input = response.first_entry.leaf_input
        # print(leaf_input.version)
        timestamped_entry = leaf_input.timestamped_entry
        print(timestamped_entry.entry_type)
        # print(timestamped_entry.extensions)

        print(hexdump(timestamped_entry.tdf))

        sct_version = rfc6962.Version(b'\x00')
        signature_type = rfc6962.SignatureType(b'\x00')

        # print(sct_version)
        # print(sct_version.tdf)
        # print(signature_type)
        # print(signature_type.tdf)

        signature_input = \
            sct_version.tdf + signature_type.tdf + timestamped_entry.tdf

        # print(hexdump(signature_input))

        pubkey = get_pubkey_pem(string_without_prefix('https://', ctlog_url))
        # print(pubkey)

        signature = decode_from_b64(signature_b64)

        verified, output, cmd_res = verify_signature(
            signature_input,
            signature,
            pubkey
        )
        print('--')
        print(verified)
        print('--')


def main():
    parser = create_parser()
    args = parser.parse_args()
    logger = setup_logging(args.loglevel)
    logger.debug(args)

    get_entry(
        index=args.entry, ctlog_url=args.log, signature_b64=args.signature)


if __name__ == '__main__':
    main()
