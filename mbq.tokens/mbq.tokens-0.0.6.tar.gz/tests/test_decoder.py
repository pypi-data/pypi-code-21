import calendar
import datetime as dt
from unittest import TestCase

import jwt

from mbq import tokens
from tests import keys
from tests.compat import mock


def since_epoch():
    return calendar.timegm(dt.datetime.utcnow().utctimetuple())


def make_jwt(audience=None):
    now = dt.datetime.utcnow()
    claims = {
        'aud': audience or 'test_audience',
        'iat': now,
        'exp': now + dt.timedelta(minutes=1),
        'iss': 'https://example.auth0.com/',
        'sub': 'abc123|test@example.com',
    }
    return jwt.encode(claims, keys.PRIVATE_KEY, algorithm='RS256')


class DecoderTest(TestCase):

    def test_init_certificate_required(self):
        with self.assertRaises(tokens.TokenError):
            tokens.Decoder(allowed_audiences=[])

    def test_init_certificate_valid(self):
        with self.assertRaises(tokens.TokenError):
            tokens.Decoder(certificate='test', allowed_audiences=[])

    def test_init_allowed_audiences(self):
        with self.assertRaises(tokens.TokenError):
            tokens.Decoder(certificate=keys.CERTIFICATE, allowed_audiences='test')

        with self.assertRaises(tokens.TokenError):
            tokens.Decoder(certificate=keys.CERTIFICATE, allowed_audiences=[1, 2, 3])

        audiences = ['test1', 'test2', 'test3']
        tokens.Decoder(certificate=keys.CERTIFICATE, allowed_audiences=set(audiences))
        tokens.Decoder(certificate=keys.CERTIFICATE, allowed_audiences=list(audiences))
        tokens.Decoder(certificate=keys.CERTIFICATE, allowed_audiences=tuple(audiences))

    def test_decode_garbage_does_not_decode(self):
        decoder = tokens.Decoder(certificate=keys.CERTIFICATE, allowed_audiences={'test_audience'})
        with self.assertRaises(tokens.TokenError):
            decoder.decode('garbage data')

    def test_decode_bad_audience(self):
        decoder = tokens.Decoder(certificate=keys.CERTIFICATE, allowed_audiences={'test_audience'})
        with self.assertRaises(tokens.TokenError):
            decoder.decode(make_jwt(audience='different_audience'))

    def test_decode(self):
        decoder = tokens.Decoder(certificate=keys.CERTIFICATE, allowed_audiences={'test_audience'})
        decoded_token = decoder.decode(make_jwt())
        self.assertEqual(decoded_token['aud'], 'test_audience')
        self.assertEqual(decoded_token['iss'], 'https://example.auth0.com/')
        self.assertEqual(decoded_token['sub'], 'abc123|test@example.com')

        now = since_epoch()
        self.assertGreaterEqual(now, decoded_token['iat'])
        self.assertGreater(decoded_token['exp'], now)

    def test_decode_header_bad_header(self):
        decoder = tokens.Decoder(certificate=keys.CERTIFICATE, allowed_audiences={'test'})
        decoder.decode = mock.MagicMock()

        with self.assertRaises(tokens.TokenError):
            decoder.decode_header(None)
        self.assertEqual(decoder.decode.call_count, 0)

        with self.assertRaises(tokens.TokenError):
            decoder.decode_header('test')
        self.assertEqual(decoder.decode.call_count, 0)

        with self.assertRaises(tokens.TokenError):
            decoder.decode_header('test test test')
        self.assertEqual(decoder.decode.call_count, 0)

        with self.assertRaises(tokens.TokenError):
            # doesn't start with Bearer
            decoder.decode_header('test test')
        self.assertEqual(decoder.decode.call_count, 0)

    def test_decode_header_extra_whitespace(self):
        decoder = tokens.Decoder(certificate=keys.CERTIFICATE, allowed_audiences={'test'})
        decoder.decode = mock.MagicMock()

        decoder.decode_header('   Bearer     test  ')
        args, kwargs = decoder.decode.call_args
        self.assertEqual(args[0], 'test')

    def test_decode_header_case_insensitive_bearer(self):
        decoder = tokens.Decoder(certificate=keys.CERTIFICATE, allowed_audiences={'test'})
        decoder.decode = mock.MagicMock()

        decoder.decode_header('bearer test')
        args, kwargs = decoder.decode.call_args
        self.assertEqual(args[0], 'test')
