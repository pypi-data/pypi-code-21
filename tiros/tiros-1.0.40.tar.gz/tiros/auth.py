from __future__ import absolute_import, division, print_function, unicode_literals

import hashlib
import hmac

import tiros.util as util


def sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def get_signature_key(key, date, region, service):
    k_date = sign(('AWS4' + key).encode('utf-8'), date)
    k_region = sign(k_date, region)
    k_service = sign(k_region, service)
    return sign(k_service, 'aws4_request')


class Signer:
    """
    A record with sufficient information to create a sigv4 signature and
    authorization header for an HTTP request.

    See: http://docs.aws.amazon.com/general/latest/gr/sigv4-signed-request-examples.html
    """
    def __init__(self, access_key, amz_date, body, date_stamp, host, method,
                 region, route, secret_key):
        assert date_stamp
        assert region
        # Host must be lower case (for authentication)
        host = host.lower()
        algorithm = 'AWS4-HMAC-SHA256'
        canonical_querystring = ''
        service = 'tiros'
        signed_headers = 'content-type;host;x-amz-date'
        canonical_headers = (
            'content-type:{}\nhost:{}\nx-amz-date:{}\n'.format(
                util.CONTENT_TYPE, host, amz_date))
        payload_hash = hashlib.sha256(body.encode()).hexdigest()
        canonical_request = '\n'.join(
            [method, route, canonical_querystring, canonical_headers,
             signed_headers, payload_hash])
        credential_scope = '/'.join(
            [date_stamp, region, service, 'aws4_request'])
        string_to_sign = '\n'.join(
            [algorithm, amz_date, credential_scope,
             hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()])
        signing_key = get_signature_key(
            secret_key, date_stamp, region, service)
        credential = ''.join([access_key, '/', credential_scope])
        self.signature = hmac.new(
            signing_key, string_to_sign.encode('utf-8'),
            hashlib.sha256).hexdigest()
        # NB: It's important to quote the auth header, since it has characters
        # not generally legal for HTTP headers like '/'
        self.authorization_header = ''.join([
            algorithm,
            ' Credential=', util.quote(credential),
            ', SignedHeaders=', util.quote(signed_headers),
            ', Signature=', self.signature
        ])


class AuthSession:
    """
    A record of the components of an AWS profile.  It's essentially the
    same record as a boto3.Session, so there are convenience methods
    to change back and forth.  It also supports the read syntax
    profile-name/region.
    """
    def __init__(self, session):
        assert session.region_name, 'session needs a region for auth'
        self.session = session

    def access_key(self):
        return self.session.get_credentials().access_key

    def secret_key(self):
        return self.session.get_credentials().secret_key

    def token(self):
        return self.session.get_credentials().token

    def region(self):
        return self.session.region_name

    def _signer(self, amz_date, body, date_stamp, host, method, route):
        return Signer(access_key=self.access_key(),
                      amz_date=amz_date,
                      body=body,
                      date_stamp=date_stamp,
                      host=host,
                      method=method,
                      region=self.region(),
                      route=route,
                      secret_key=self.secret_key())

    def auth_header(self, amz_date, body, date_stamp, host, method, route):
        return self._signer(amz_date, body, date_stamp, host, method, route).authorization_header

    def request_key(self, amz_date, body, date_stamp, host, method, route):
        obj = {
            'accessKeyId': self.access_key(),
            'amzDate': amz_date,
            'body': body,
            'host': host,
            'method': method,
            'region': self.region(),
            'route': route,
            'signature': self._signer(amz_date, body, date_stamp, host, method, route).signature
        }
        # Python encodes None in JSON as "None", not null
        if self.token():
            obj['sessionToken'] = self.token()
        return obj

    def snapshot_key(self, amz_date, date_stamp, host):
        return self.request_key(amz_date, '', date_stamp, host, util.METHOD,
                                'snapshot')
