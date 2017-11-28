# coding=utf-8
# ***** BEGIN LICENSE BLOCK *****
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
# ***** END LICENSE BLOCK *****

import os.path
import shutil
import tempfile
import unittest
import collections
import datetime

from hashlib import sha1
import asn1crypto
from asn1crypto.util import timezone

from signing_clients.apps import (
    force_bytes,
    Manifest,
    JarExtractor,
    ParsingError,
    ZipFile,
    file_key,
    get_signer_serial_number,
    ignore_certain_metainf_files,
    get_signer_organizational_unit_name,
    SignatureInfo
)

from signing_clients import constants


MANIFEST_BODY = b"""Name: test-file
Digest-Algorithms: MD5 SHA1
MD5-Digest: 5BXJnAbD0DzWPCj6Ve/16w==
SHA1-Digest: 5Hwcbg1KaPMqjDAXV/XDq/f30U0=

Name: test-dir/nested-test-file
Digest-Algorithms: MD5 SHA1
MD5-Digest: 53dwfEn/GnFiWp0NQyqWlA==
SHA1-Digest: 4QzlrC8QyhQW1T0/Nay5kRr3gVo=
"""

MANIFEST = b"Manifest-Version: 1.0\n\n" + MANIFEST_BODY

SIGNATURE = b"""Signature-Version: 1.0
MD5-Digest-Manifest: A3IkNTcP2L6JzwQzkp+6Kg==
SHA1-Digest-Manifest: xQKf9C1JcIjfZoFxTWt3pzW2KYI=

"""

CONTINUED_MANIFEST = MANIFEST + b"""
Name: test-dir/nested-test-dir/nested-test-dir/nested-test-dir/nested-te
 st-file
Digest-Algorithms: MD5 SHA1
MD5-Digest: 53dwfEn/GnFiWp0NQyqWlA==
SHA1-Digest: 4QzlrC8QyhQW1T0/Nay5kRr3gVo=
"""

# Test for 72 byte limit test
BROKEN_MANIFEST = MANIFEST + b"""
Name: test-dir/nested-test-dir/nested-test-dir/nested-test-dir/nested-test-file
Digest-Algorithms: MD5 SHA1
MD5-Digest: 53dwfEn/GnFiWp0NQyqWlA==
SHA1-Digest: 4QzlrC8QyhQW1T0/Nay5kRr3gVo=
"""

VERY_LONG_MANIFEST = b"""Manifest-Version: 1.0

Name: test-file
Digest-Algorithms: MD5 SHA1
MD5-Digest: 5BXJnAbD0DzWPCj6Ve/16w==
SHA1-Digest: 5Hwcbg1KaPMqjDAXV/XDq/f30U0=

Name: test-dir/nested-test-file
Digest-Algorithms: MD5 SHA1
MD5-Digest: 53dwfEn/GnFiWp0NQyqWlA==
SHA1-Digest: 4QzlrC8QyhQW1T0/Nay5kRr3gVo=

Name: test-dir/nested-test-dir-0/nested-test-dir-1/nested-test-dir-2/lon
 g-path-name-test
Digest-Algorithms: MD5 SHA1
MD5-Digest: 9bU/UEp83EbO/DWN3Ds/cg==
SHA1-Digest: lIbbwE8/2LFOD00+bJ/Wu80lR/I=

"""

# Test for Unicode
UNICODE_MANIFEST = u"""Manifest-Version: 1.0

Name: test-dir/súité-höñe.txt
Digest-Algorithms: MD5 SHA1
MD5-Digest: +ZqzWWcMtOrWxs8Xr/tt+A==
SHA1-Digest: B5HkCxgt6fXNr+dWPwXH2aALVWk=
"""


def get_file(fname):
    return os.path.join(os.path.dirname(__file__), fname)


class SigningTest(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix='tmp-signing-clients-test-')
        self.addCleanup(lambda: shutil.rmtree(self.tmpdir))

    def tmp_file(self, fname):
        return os.path.join(self.tmpdir, fname)

    def _extract(self):
        return JarExtractor(get_file('test-jar.zip'))

    def test_extractor(self):
        self.assertTrue(isinstance(self._extract(), JarExtractor))

    def test_manifest(self):
        extracted = self._extract()
        self.assertEqual(force_bytes(extracted.manifest), MANIFEST + b"\n")

    def test_signature(self):
        extracted = self._extract()
        self.assertEqual(force_bytes(extracted.signature), SIGNATURE)

    def test_signatures(self):
        extracted = self._extract()
        self.assertEqual(force_bytes(extracted.signatures), SIGNATURE)

    def test_continuation(self):
        manifest = Manifest.parse(CONTINUED_MANIFEST)
        self.assertEqual(force_bytes(manifest), CONTINUED_MANIFEST + b"\n")

    def test_line_too_long(self):
        self.assertRaises(ParsingError, Manifest.parse, BROKEN_MANIFEST)

    def test_wrapping(self):
        extracted = JarExtractor(get_file('test-jar-long-path.zip'))
        self.assertEqual(force_bytes(extracted.manifest), VERY_LONG_MANIFEST)

    def test_unicode(self):
        extracted = JarExtractor(get_file('test-jar-unicode.zip'))
        self.assertEqual(
            force_bytes(extracted.manifest).decode('utf-8'), UNICODE_MANIFEST + u"\n")

    def test_serial_number_extraction(self):
        with open(get_file('zigbert.test.pkcs7.der'), 'rb') as f:
            serialno = get_signer_serial_number(f.read())
        # Signature occured on Thursday, January 22nd 2015 at 11:02:22am PST
        # The signing service returns a Python time.time() value multiplied
        # by 1000 to get a (hopefully) truly unique serial number
        self.assertEqual(1421953342960, serialno)

    def test_serial_number_extraction(self):
        with open(get_file('mozilla-generated-by-openssl.pkcs7.der'), 'rb') as f:
            serialno = get_signer_serial_number(f.read())
        self.assertEqual(1498181554500, serialno)

    def test_resigning_manifest_exclusions(self):
        # This zip contains META-INF/manifest.mf, META-INF/zigbert.sf, and
        # META-INF/zigbert.rsa in addition to the contents of the basic test
        # archive test-jar.zip
        extracted = JarExtractor(get_file('test-jar-meta-inf-exclude.zip'))
        self.assertEqual(force_bytes(extracted.manifest), MANIFEST + b"\n")

    def test_make_signed(self):
        extracted = JarExtractor(get_file('test-jar.zip'))
        # Not a valid signature but a PKCS7 data blob, at least
        with open(get_file('zigbert.test.pkcs7.der'), 'rb') as f:
            signature = f.read()
            signature_digest = sha1()
            signature_digest.update(signature)

        signed_file = self.tmp_file('test-jar-signed.zip')
        sigpath = 'zoidberg'
        extracted.make_signed(
            signed_manifest=str(extracted.signatures),
            signature=signature,
            outpath=signed_file,
            sigpath=sigpath
        )
        # Now verify the signed zipfile's contents
        with ZipFile(signed_file, 'r') as zin:
            # sorted(...) should result in the following order:
            files = ['test-file', 'META-INF/manifest.mf',
                     'META-INF/zoidberg.rsa',
                     'META-INF/zoidberg.sf',
                     'test-dir/', 'test-dir/nested-test-file']
            zfiles = sorted([z.filename for z in zin.filelist], key=file_key)
            self.assertEqual(files, zfiles)
            zip_sig_digest = sha1()
            zip_sig_digest.update(zin.read('META-INF/zoidberg.rsa'))

            self.assertEqual(signature_digest.hexdigest(),
                             zip_sig_digest.hexdigest())
        # And make sure the manifest is correct
        signed = JarExtractor(signed_file)
        self.assertEqual(force_bytes(extracted.manifest), force_bytes(signed.manifest))

    def test_make_signed_default_sigpath(self):
        extracted = JarExtractor(get_file('test-jar.zip'))
        # Not a valid signature but a PKCS7 data blob, at least
        with open(get_file('zigbert.test.pkcs7.der'), 'rb') as f:
            signature = f.read()
            signature_digest = sha1()
            signature_digest.update(signature)

        signed_file = self.tmp_file('test-jar-signed.zip')
        extracted.make_signed(
            signed_manifest=str(extracted.signatures),
            signature=signature,
            outpath=signed_file,
            sigpath='zigbert'
        )

        with ZipFile(signed_file, 'r') as zin:
            files = ['test-file', 'META-INF/manifest.mf',
                     'META-INF/zigbert.rsa',
                     'META-INF/zigbert.sf',
                     'test-dir/', 'test-dir/nested-test-file']
            zfiles = sorted([z.filename for z in zin.filelist], key=file_key)
            self.assertEqual(files, zfiles)
            zip_sig_digest = sha1()
            zip_sig_digest.update(zin.read('META-INF/zigbert.rsa'))

            self.assertEqual(signature_digest.hexdigest(),
                             zip_sig_digest.hexdigest())

        signed = JarExtractor(signed_file)
        self.assertEqual(force_bytes(extracted.manifest), force_bytes(signed.manifest))

    def test_make_signed_refuses_weird_sigpath(self):
        extracted = JarExtractor(get_file('test-jar.zip'))

        # Hardcode the parameters we don't care about in this test
        signed_manifest = 'abc'
        signature = 'signed: abc'
        outpath = 'signed-jar.zip'

        def make_signed(sigpath):
            return extracted.make_signed(
                signed_manifest=signed_manifest,
                signature=signature,
                outpath=outpath,
                sigpath=sigpath
            )

        self.assertRaises(ValueError, make_signed, 'subdirectory/filename')
        self.assertRaises(ValueError, make_signed, 'filename.abc')


    # See https://bugzil.la/1169574
    def test_metainf_case_sensitivity(self):
        self.assertTrue(ignore_certain_metainf_files('meta-inf/manifest.mf'))
        self.assertTrue(ignore_certain_metainf_files('MeTa-InF/MaNiFeSt.Mf'))
        self.assertFalse(ignore_certain_metainf_files('meta-inf/pickles.mf'))

    def test_get_signer_organizational_unit_name(self):
        with open(get_file('mozilla-generated-by-openssl.pkcs7.der'), 'rb') as f:
            addon_type = get_signer_organizational_unit_name(f.read())

        self.assertEqual(addon_type, 'Testing')

        with open(get_file('webextension_signed.rsa'), 'rb') as f:
            addon_type = get_signer_organizational_unit_name(f.read())

        self.assertEqual(addon_type, 'Mozilla Extensions')

        with open(get_file('zigbert.test.pkcs7.der'), 'rb') as f:
            addon_type = get_signer_organizational_unit_name(f.read())

        self.assertEqual(addon_type, 'Mozilla Addons Dev')


class TestSignatureInfo(unittest.TestCase):

    def setUp(self):
        with open(get_file('mozilla-generated-by-openssl.pkcs7.der'), 'rb') as f:
            self.pkcs7 = f.read()

        self.info = SignatureInfo(self.pkcs7)

    def test_loading_reading_string(self):
        info = SignatureInfo(self.pkcs7)
        self.assertTrue(isinstance(info.content, collections.OrderedDict))

    def test_loading_pass_signature_info_instance(self):
        info = SignatureInfo(self.pkcs7)
        self.assertTrue(isinstance(info.content, collections.OrderedDict))

        info2 = SignatureInfo(info)

        self.assertTrue(isinstance(info2.content, collections.OrderedDict))
        self.assertEqual(info2.content, info.content)

    def test_signer_serial_number(self):
        self.assertEqual(self.info.signer_serial_number, 1498181554500)

    def test_issuer(self):
        self.assertEqual(self.info.issuer, collections.OrderedDict([
            ('country_name', 'US'),
            ('state_or_province_name', 'CA'),
            ('locality_name', 'Mountain View'),
            ('organization_name', 'Addons Test Signing'),
            ('common_name', 'test.addons.signing.root.ca'),
            ('email_address', 'opsec+stagerootaddons@mozilla.com')
        ]))

    def test_signer_certificate(self):
        self.assertEqual(
            self.info.signer_certificate['serial_number'],
            self.info.signer_serial_number)
        self.assertEqual(self.info.signer_certificate['issuer'], self.info.issuer)

        self.assertEqual(self.info.signer_certificate, collections.OrderedDict([
            ('version', 'v3'),
            ('serial_number', 1498181554500),
            ('signature', collections.OrderedDict([
            ('algorithm', 'sha256_rsa'), ('parameters', None)])),
            ('issuer', collections.OrderedDict([
                ('country_name', 'US'),
                ('state_or_province_name', 'CA'),
                ('locality_name', 'Mountain View'),
                ('organization_name', 'Addons Test Signing'),
                ('common_name', 'test.addons.signing.root.ca'),
                ('email_address', 'opsec+stagerootaddons@mozilla.com')])),
            ('validity', collections.OrderedDict([
                ('not_before',
                 datetime.datetime(2017, 6, 23, 1, 32, 34, tzinfo=timezone.utc)),
                ('not_after',
                 datetime.datetime(2027, 6, 21, 1, 32, 34, tzinfo=timezone.utc))])),
            ('subject', collections.OrderedDict([
                ('organizational_unit_name', 'Testing'),
                ('country_name', 'US'),
                ('locality_name', 'Mountain View'),
                ('organization_name', 'Addons Testing'),
                ('state_or_province_name', 'CA'),
                ('common_name', '{02b860db-e71f-48d2-a5a0-82072a93d33c}')])),
            ('subject_public_key_info', collections.OrderedDict([
                ('algorithm', collections.OrderedDict([
                    ('algorithm', 'rsa'),
                    ('parameters', None)])),
                    ('public_key', collections.OrderedDict([
                        ('modulus', int(
                            '85289209018591781267198931558814435907521407777661'
                            '50749316736213617395458578680335589192171418852036'
                            '79278813048882998104120530700223207250951695884439'
                            '20772452388935409377024686932620042402964287828106'
                            '51257320080972660594945900464995547687116064792520'
                            '10385231846333656801523388692257373069803424678966'
                            '83558316878945090150671487395382420988138292553386'
                            '65273893489909596214808207811839117255018821125538'
                            '88010045768747055709235990054867405484806043609964'
                            '46844151945633093802308152276459710592644539761011'
                            '95743982561110649516741370965629194907895538590306'
                            '29899529219665410153860752870947521013079820756069'
                            '47104737107240593827799410733495909560358275915879'
                            '55064950558358425436354620230911526069861662920050'
                            '43124539276872288437450042840027281372269967539939'
                            '24111213120065958637042429018593980801963496240784'
                            '12170983502746046961830237201163411151902047596357'
                            '52875610569157058411595354595985036610666909234931'
                            '24897289875099542550941258245633054592232417696315'
                            '40182071794766323211615139265042704991415186206585'
                            '75885408887756385761663648099801365729955339334103'
                            '60468108188015261735738849468668895508239573547213'
                            '28312488126574859733988724870493942605656816541143'
                            '61628373225003401044258905283594542783785817504173'
                            '841847040037917474056678747905247')),
                        ('public_exponent', 65537)]))])),
            ('issuer_unique_id', None),
            ('subject_unique_id', None),
            ('extensions', None)]))
