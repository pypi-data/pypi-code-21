from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate
import jwt
import six

from . import exceptions


class Decoder:
    def __init__(self, certificate=None, allowed_audiences=None):
        if not certificate:
            m = ('`certificate` must be a string with proper key guards '
                 '(i.e., -----BEGIN CERTIFICATE-----)')
            raise exceptions.TokenError(m)

        err_msg = '`allowed_audiences` must be a list, tuple, or set of strings'
        if not isinstance(allowed_audiences, (list, tuple, set)):
            raise exceptions.TokenError(err_msg)

        if any(not isinstance(aud, six.string_types) for aud in allowed_audiences):
            raise exceptions.TokenError(err_msg)

        try:
            self._public_key = load_pem_x509_certificate(
                certificate.encode(),
                default_backend(),
            ).public_key()
        except Exception as e:
            msg = '`certificate` could not be loaded as a public key. {}'.format(e)
            raise exceptions.TokenError(msg)

        self._allowed_audiences = set(allowed_audiences)

    def decode(self, token):
        try:
            decoded_token = jwt.decode(
                token,
                key=self._public_key,
                options={'verify_aud': False},
                algorithms=['RS256'],
            )
        except Exception as e:
            msg = '`token` could not be decoded. {}'.format(e)
            raise exceptions.TokenError(msg)

        if decoded_token['aud'] not in self._allowed_audiences:
            raise exceptions.TokenError('`aud` claim is not in allowed_audiences')

        return decoded_token

    def decode_header(self, header):
        err_msg = '`header` must be a string in the form "Bearer <token>"'

        if not isinstance(header, six.string_types):
            raise exceptions.TokenError(err_msg)

        try:
            bearer, token = header.strip().split()
        except ValueError:
            raise exceptions.TokenError(err_msg)

        if bearer.lower() != 'bearer':
            raise exceptions.TokenError(err_msg)

        return self.decode(token)
