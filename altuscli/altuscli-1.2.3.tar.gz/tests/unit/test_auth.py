# Copyright 2012-2013 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Modifications made by Cloudera are:
#     Copyright (c) 2016 Cloudera, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
from base64 import urlsafe_b64decode
import datetime

from altuscli.altusrequest import AltusRequest
import altuscli.auth
from altuscli.compat import HTTPHeaders
from altuscli.compat import json
from altuscli.compat import urlsplit
import altuscli.credentials
from altuscli.exceptions import NoCredentialsError
import mock
from tests import unittest


RSA_KEY = \
    """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCsdjjYZKA3pqzj
XXZq2NidIg9UE3oGajYXftpiTVS3vJtfrK38202r3YbrMdAtzSm5BzVHU74C2XVX
RWrCZ9Js9Dh3RYta7uqh9b1PNdJIP+/fUBJZs5eJ+oMkTbmtgFznprUi7RcrU9Pb
k9ByIqnaJv6Dw/1SvsbwAIjbAyqNXP0WJvFc0hznHu5Ok3US8uz+fdIbalPSEKgN
6fmYmhabaGUbXmMrUevtIL9BRUY7/3vCR+vm+6UKfQqS4knMYLZN7NjIl4t/WvTX
RfuhObpgaD1c3S0LmFwFeTAmguG2tbSNDzkzG9tN3zuVxtL0+Sy/I3f+kHEVkDQW
CnnGRhBRAgMBAAECggEAbgILSJ0HRfhfl7hqbMVdhv3O4UZ7M9RUJLCaBNJnE7yP
L3wqj3wkE1j/Us83h7+yuX/LkG/uaErl+oEhFFi9dRpjWlFWDu8PY7goxXoDZGrE
S6H70pQoOa8+L84UfoO+v1UrfdfWS6DxJsMm12cdCTaOauZ9lGZ052qv4WQnpHt7
K9asyrsGSE4W1aKHIPUGbreOfwELDH/PkLLHsbVnC5PG6jpQaJHUEoebkQkVW7Ru
mG4AwH26HTNoVF5YPGSy0BRHab+0mrh4X2HHBTyzKEWQUYlWQlfW9iekmkdbrELr
adhqanguSwVUm6jrn4CRn6M2Wn55/Jv8LytlGUpBcQKBgQDAcPg74uwcz4Yoc6OM
uKVCxqwL5fOvxpVSc4+u07KCbX6tPsEXvCiPs30/a71xwcP42QBt9aLqRd8C+z99
ri36LNNLRc9/SH3TmezzXhuBK3nkX3pT6zJuiX+T5WrUueOyANUm0d9cvQsrH6uF
LtK9rXG4WKPH223QqBEPhv4yqwKBgQDla/mGm620PATZ6yUIfmJLLZF3fWiqekfk
2R6kyUhUm672mzqi1xTOByfobMjsel5UXW6gzwm9qkBG47OrvjINyq+ja/UOO4kq
ZtqlgNkL4nN5y2GTXbJrG7eabgsB3nq1+IvDC+dFTPqSuJoYfoZZtT58eMAHGTmh
Ka8ehzPo8wKBgExyFAomIMlpHtAe789M4klehqXLWTxwVI0GXwOCER2CxZmonigB
lNNQ5+YztHPmFyVZfrQvqeIKk4aprBUPBjClceIq/zx+3Y0bTmd28NIlJSy1SPDh
M415jXaA4ilTFsJ1Vjcvk91RM4iT8hzb9tdmeRBUFeuknUEQIobah0w1AoGBAKpW
f97sqYz/Xw65ozZqN+rfe3j/eP3SapzEhBcPh4+iQ8a/vEp5bO4HrB7K3meN94mm
EWR+NBpJVQ4NNDKYtas9ySiKGFmn5JDB6yckwoIrcVeFpP34fGdAHhMgDzYlDHEd
iA+aP+1ZWVYkj+0NzAzBIBLkyJa8qOg6/dWpxuX3AoGAYW0qU+s8bumhvxPEMbfQ
zU0IHNaprGxO+yZuMvdyfxcJVuFQf22mujPI8GluXyfA5i2IZjScNf5Awccu8HS5
mzJp12+5oAZ+tJE1scpVoaVdZloY8XA1u0aCt2BhZavjIizTyzY4L8clo2iGIO1x
yj5v7z/1wWTorT4w3/IHcwM=
-----END PRIVATE KEY-----"""

EXPECTED_SIG = \
    'VLlOczaMiHdAHfW7-0axYWAxpFPqHR2sR22XRh98AlVTBjj8QJTModpzNUQxb1N0F94pMP6U' \
    'BI-flm-rl3vHJaRBfcWbaDglD02YcuqD87CmOIpZ6Z3TUTbkOcxTsMSkgOaPqQkO1p49WRl3' \
    'P_v3Q9z5y6Mh7ZDbQeonQcagKhoIYQnCXYrEmAAHhTGwuxanuAsPu2y8svUBKNd9fXZ7stQ0' \
    'Pom2J2aQZnegBM6I_QJICP7ZEd0Roga0AcGoL1OsZo_fANkUV9eUvtw8CfTw11G2c1YS__pq' \
    'PVuW4iPSYONoUN5NrL6x3RtGOea0Xo__9B5ki0_TLsYMyhF37it6qA=='


class BaseTestWithFixedDate(unittest.TestCase):
    def setUp(self):
        self.datetime_patch = mock.patch('altuscli.auth.datetime')
        self.datetime_mock = self.datetime_patch.start()
        self.fixed_date = datetime.datetime(2014, 3, 10, 17, 2, 55, 0)
        self.datetime_mock.datetime.utcnow.return_value = self.fixed_date
        self.datetime_mock.datetime.strptime.return_value = self.fixed_date

    def tearDown(self):
        self.datetime_patch.stop()


class TestBaseSigner(unittest.TestCase):
    def test_base_signer_raises_error(self):
        base_signer = altuscli.auth.BaseSigner()
        with self.assertRaises(NotImplementedError):
            base_signer.add_auth("pass someting")


class TestRSAV1(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        access_key_id = 'ABCD-EFGH-IJKL-MNOP-QRST'
        self.credentials = altuscli.credentials.Credentials(
            access_key_id,
            RSA_KEY,
            'test')
        self.rsav1 = altuscli.auth.RSAv1Auth(self.credentials)
        self.date_mock = mock.patch('altuscli.auth.formatdate')
        self.formatdate = self.date_mock.start()
        self.formatdate.return_value = 'Thu, 17 Nov 2005 18:49:58 GMT'

    def tearDown(self):
        self.date_mock.stop()

    def test_put(self):
        http_headers = HTTPHeaders.from_dict({})
        split = urlsplit('/foo/bar')
        cs = self.rsav1._canonical_string('PUT', split, http_headers)
        expected_canonical = "PUT\n\nThu, 17 Nov 2005 18:49:58 GMT\n/foo/bar\nrsav1"
        self.assertEqual(expected_canonical, cs)
        sig = self.rsav1._get_signature('PUT', split, HTTPHeaders.from_dict({}))
        self.assertEqual(EXPECTED_SIG, sig)

    def test_duplicate_date(self):
        pairs = [('x-altus-date', 'Thu, 17 Nov 2015 18:49:58 GMT'),
                 ('X-Altus-Magic', 'abracadabra')]
        http_headers = HTTPHeaders.from_pairs(pairs)
        split = urlsplit('/foo/bar')
        with self.assertRaises(Exception):
            self.rsav1.get_signature('PUT', split, http_headers)

    def test_duplicate_auth_header(self):
        request = AltusRequest()
        request.headers = HTTPHeaders.from_dict({'x-altus-auth': 'signature'})
        request.method = 'PUT'
        request.url = 'https://altus.cloudera.com/service/op'
        with self.assertRaises(Exception):
            self.rsav1._inject_signature(request, 'new_signature')

    def test_resign_uses_most_recent_date(self):
        dates = [
            'Thu, 17 Nov 2005 18:49:58 GMT',
            'Thu, 17 Nov 2014 20:00:00 GMT',
        ]
        self.formatdate.side_effect = dates

        request = AltusRequest()
        request.headers['Content-Type'] = 'text/html'
        request.method = 'PUT'
        request.url = 'https://altus.cloudera.com/service/op'

        self.rsav1.add_auth(request)
        original_date = request.headers['x-altus-date']

        del request.headers['x-altus-date']
        del request.headers['x-altus-auth']
        self.rsav1.add_auth(request)
        modified_date = request.headers['x-altus-date']

        # Each time we sign a request, we make another call to formatdate()
        # so we should have a different date header each time.
        self.assertEqual(original_date, dates[0])
        self.assertEqual(modified_date, dates[1])

    def test_no_credentials_raises_error(self):
        rsav1 = altuscli.auth.RSAv1Auth(None)
        with self.assertRaises(NoCredentialsError):
            rsav1.add_auth("pass someting")

    def test_auth_header_string(self):
        http_headers = HTTPHeaders.from_dict({})
        split = urlsplit('/foo/bar')
        sig = self.rsav1._get_signature('PUT', split, http_headers)
        self.assertEqual(EXPECTED_SIG, sig)

        auth_header_string = self.rsav1._get_signature_header(sig)
        expected_metadata = 'eyJhY2Nlc3Nfa2V5X2lkIjogIkFCQ0QtRUZHSC1JSktMLU1O' \
                            'T1AtUVJTVCIsICJhdXRoX21ldGhvZCI6ICJyc2F2MSJ9'
        metadata, sig = auth_header_string.split(".")
        self.assertEqual(expected_metadata, metadata)
        self.assertEqual(EXPECTED_SIG, sig)

        json_metadata = json.loads(
            urlsafe_b64decode(metadata.encode('utf-8')).decode('utf-8'))
        self.assertEqual(self.credentials.access_key_id,
                         json_metadata['access_key_id'])
        self.assertEqual("rsav1",
                         json_metadata['auth_method'])
