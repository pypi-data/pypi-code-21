'''Construct and verify an SCT for a certificate from the add-chain response of
a Certificate Transparency (CT) log (cf.
https://tools.ietf.org/html/rfc6962#section-4.1).
'''

# -*- coding: utf-8 -*-

import argparse
import json
import logging

from utlz import flo, first_paragraph, load_json, namedtuple

from ctutlz.utils.logger import loglevel, setup_logging
from ctutlz.ctlog import Log
from ctutlz.sct.sct import _Sct
from ctutlz.sct.ee_cert import EndEntityCert, IssuerCert
from ctutlz.sct.signature_input import create_signature_input_precert
from ctutlz.sct.verification import verify_signature, SctValidationResult
from ctutlz.utils.encoding import decode_from_b64


# TODO FIXME: refactor code
# there should be a signature_input(.. ct_log_resp ..) function
def sct_from_log_response(ct_log_response):
    data_dict = {
        'der': None,

        # 'log_id': decode_from_b64(ct_log_response.id.encode('ascii')),
        'log_id': decode_from_b64(ct_log_response.id),
        'extensions': None,
        'signature_alg_hash': int(0),  # doesn't matter
        'signature_alg_sign': int(0),  # doesn't matter
        'signature_len': None,
        # 'signature': bytes(ct_log_response.signature, 'ascii'),
        'signature': decode_from_b64(ct_log_response.signature),

        # required for signature input creation
        'version': int(ct_log_response.sct_version),
        'timestamp': int(ct_log_response.timestamp),
        'extensions_len': len(ct_log_response.extensions),
    }
    return _Sct(**data_dict)


CtLogResponse = namedtuple(
    typename='CtLogResponse',
    field_names=[
        'extensions',
        'id',
        'sct_version',
        'signature',
        'timestamp',
    ]
)


def create_and_validate_sct_of_precert(ee_cert, issuer_cert, ct_log_response,
                                       log_key_str_b64):
    sct = sct_from_log_response(ct_log_response)

    sign_input_func = create_signature_input_precert

    log = Log(
        description=None,
        key=log_key_str_b64,
        url=None,
        maximum_merge_delay=None,
        operated_by=[''],
    )

    # TODO DEBUG
    print(log.pubkey)
    print(log.pubkey.encode('ascii'))
    signature_input = sign_input_func(ee_cert, sct, issuer_cert)
    open('charon/signature_input.bin', 'wb').write(signature_input)
    import base64

    verified, output, cmd_res = verify_signature(
        signature_input=sign_input_func(ee_cert, sct, issuer_cert),
        signature=sct.signature,
        pubkey=log.pubkey.encode('ascii')
    )
    return SctValidationResult(ee_cert, sct, log, verified, output, cmd_res)


def create_and_validate_sct_of_cert(ee_cert, ct_log_response, log_key_str_b64):
    raise(Exception('not implemented'))


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
    req.add_argument('--cert',
                     metavar='<file>',
                     required=True,
                     help='end entity certificate of the chain submitted to '
                          'the CT log encoded as DER or PEM, or a chain '
                          'containing the precert followed by its issuer cert')
    req.add_argument('--resp',
                     nargs='+',
                     metavar='<file>',
                     required=True,
                     help='one or more ct-log add-chain responses '
                          'encoded as JSON objects')
    req.add_argument('--log-key',
                     nargs='+',
                     metavar='<file>',
                     required=True,
                     help='one or more log pubkeys base64 encoded')
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    logger = setup_logging(args.loglevel)
    logger.debug(args)

    with open(args.cert, 'rb') as fh:
        cert_data = fh.read()

    ee_cert_der = cert_data
    issuer_cert_der = None
    try:
        # cert comments may not are ascii-encoded
        chain_pem = cert_data.decode('utf-8')

        # FIXME: refactor
        _, ee_cert_and_rest = chain_pem.split(
            '-----BEGIN CERTIFICATE-----\n',
            1
        )
        ee_cert_b64, rest = ee_cert_and_rest.split(
            '\n-----END CERTIFICATE-----',
            1
        )
        _, issuer_and_rest = rest.split(
            '-----BEGIN CERTIFICATE-----\n',
            1
        )
        issuer_cert_b64, _ = issuer_and_rest.split(
            '\n-----END CERTIFICATE-----',
            1
        )
        ee_cert_der = decode_from_b64(ee_cert_b64)
        issuer_cert_der = decode_from_b64(issuer_cert_b64)
    except ValueError:
        pass  # swallow error, assuming DER

    ee_cert = EndEntityCert(ee_cert_der)

    with open(args.log_key[0], 'r') as fh:
        # type: str
        log_key_str_b64 = fh.read().replace(
            '-----BEGIN PUBLIC KEY-----\n', '').replace(
            '\n-----END PUBLIC KEY-----', '').replace('\n', '').replace(' ', '')

    for filename_response in args.resp:
        response_dict = load_json(filename_response)
        # with open(filename_response, 'rb') as fh:
        #     response_dict = json.load(fh)
        ct_log_response = CtLogResponse(**response_dict)

        if issuer_cert_der:
            print('** precert **')  # TODO DEBUG
            res = create_and_validate_sct_of_precert(
                ee_cert,
                IssuerCert(issuer_cert_der),
                ct_log_response,
                log_key_str_b64
            )
        else:
            print('** cert (no precert) **')  # TODO DEBUG
            res = create_and_validate_sct_of_cert(
                ee_cert,
                ct_log_response,
                log_key_str_b64
            )
        from ctutlz.scripts.verify_scts import show_validation
        show_validation(res)


if __name__ == '__main__':
    main()
