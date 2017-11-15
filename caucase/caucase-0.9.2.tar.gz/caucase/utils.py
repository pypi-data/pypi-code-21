# This file is part of caucase
# Copyright (C) 2017  Nexedi
#     Alain Takoudjou <alain.takoudjou@nexedi.com>
#     Vincent Pelletier <vincent@nexedi.com>
#
# caucase is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# caucase is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with caucase.  If not, see <http://www.gnu.org/licenses/>.
"""
Caucase - Certificate Authority for Users, Certificate Authority for SErvices

Small-ish functions needed in many places.
"""
from __future__ import absolute_import
from collections import defaultdict
import datetime
import json
import os
import time
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
import cryptography.exceptions
import pem
from .exceptions import (
  CertificateVerificationError,
  NotJSON,
)

DEFAULT_DIGEST_LIST = ('sha256', 'sha384', 'sha512')
DEFAULT_DIGEST = DEFAULT_DIGEST_LIST[0]
DEFAULT_DIGEST_CLASS = getattr(hashes, DEFAULT_DIGEST.upper())
# load-time sanity check
def _checkDefaultDigestsAvailable():
  for x in DEFAULT_DIGEST_LIST:
    getattr(hashes, x.upper())
_checkDefaultDigestsAvailable()
del _checkDefaultDigestsAvailable

_cryptography_backend = default_backend()

# Registration-less OID under 2.25 tree (aka uuid tree)
CAUCASE_OID_TOP = '2.25.285541874270823339875695650038637483517'
CAUCASE_OID_AUTO_SIGNED = CAUCASE_OID_TOP + '.0'
# Reserved for tests: no meaning, always stripped but never specificaly
# checked for in the code.
CAUCASE_OID_RESERVED = CAUCASE_OID_TOP + '.999'
_CAUCASE_OID_AUTO_SIGNED = x509.oid.ObjectIdentifier(CAUCASE_OID_AUTO_SIGNED)
CAUCASE_POLICY_INFORMATION_AUTO_SIGNED = x509.PolicyInformation(
  _CAUCASE_OID_AUTO_SIGNED,
  [
    x509.UserNotice(
      None,
      'Auto-signed caucase certificate',
    ),
  ]
)

def isCertificateAutoSigned(crt):
  """
  Checks whether given certificate was automatically signed by caucase.

  Allows ensuring no rogue certificate could be emitted before legitimate owner
  could take control of their instance: in such case, "first" certificate would
  not appear as auto-signed.

  Returns True if certificate is auto-signed, False otherwise.
  """
  try:
    extension = crt.extensions.get_extension_for_class(
      x509.CertificatePolicies,
    )
  except x509.ExtensionNotFound:
    pass
  else:
    for policy_information in extension.value:
      if policy_information.policy_identifier == _CAUCASE_OID_AUTO_SIGNED:
        return True
  return False

def _getPEMTypeDict(path, result=None):
  if result is None:
    result = defaultdict(list)
  for entry in pem.parse_file(path):
    result[pem.Key if isinstance(entry, pem.Key) else type(entry)].append(
      entry,
    )
  return result

def getCertList(crt_path):
  """
  Return a list of certificates.
  Raises if there is anything else than a certificate.
  """
  type_dict = _getPEMTypeDict(crt_path)
  crt_list = type_dict.pop(pem.Certificate)
  if type_dict:
    raise ValueError('%s contains more than just certificates' % (crt_path, ))
  return [x.as_bytes() for x in crt_list]

def getCert(crt_path):
  """
  Return a certificate from a file which may also contain a key.
  Raises if there is more or less than one certificate.
  """
  type_dict = _getPEMTypeDict(crt_path)
  crt, = type_dict.get(pem.Certificate)
  return crt.as_bytes()

def hasOneCert(crt_path):
  """
  Returns whether crt_path contains a certificate.

  False if there is no file at crt_path.
  Raises if there is more than one certificate.
  Ignores other types.
  """
  if os.path.exists(crt_path):
    crt_list = _getPEMTypeDict(crt_path).get(pem.Certificate, [])
    if crt_list:
      _, = crt_list
      return True
  return False

def getCertRequest(csr_path):
  """
  Return a certificate request from a file.
  Raises if there is more or less than one certificate request, or anything
  else.
  """
  type_dict = _getPEMTypeDict(csr_path)
  csr, = type_dict.pop(pem.CertificateRequest)
  if type_dict:
    raise ValueError('%s contains more than just a csr' % (csr_path, ))
  return csr.as_bytes()

def getKey(key_path):
  """
  Return a key from a file.
  Raises if there is more or less than one key, or anything else.
  """
  type_dict = _getPEMTypeDict(key_path)
  key, = type_dict.pop(pem.Key)
  if type_dict:
    raise ValueError('%s contains more than just a key' % (key_path, ))
  return key.as_bytes()

def getKeyPair(crt_path, key_path=None):
  """
  Return a certificate and a key from a pair of file.
  If crt_path contains both a cert and a key, key_path is ignored.
  Raises if there is more than one certificate or more than one key.
  Raises if key and cert do not match.
  """
  type_dict = _getPEMTypeDict(crt_path)
  if pem.Key not in type_dict and key_path:
    _getPEMTypeDict(key_path, type_dict)
  else:
    key_path = None
  key, = type_dict[pem.Key]
  crt, = type_dict[pem.Certificate]
  key = key.as_bytes()
  crt = crt.as_bytes()
  validateCertAndKey(crt, key)
  return crt, key, key_path

def validateCertAndKey(cert_pem, key_pem):
  """
  Verify certificate and key match.

  Raises if it is not the case.
  """
  if x509.load_pem_x509_certificate(
    cert_pem,
    _cryptography_backend,
  ).public_key().public_numbers() != load_privatekey(
    key_pem,
  ).public_key().public_numbers():
    raise ValueError('Mismatch between private key and certificate')

def _verifyCertificateChain(cert, trusted_cert_list, crl):
  """
  Verifies whether certificate has been signed by any of the trusted
  certificates, is not revoked and is whithin its validity period.

  Raises CertificateVerificationError if validation fails.
  """
  # Note: this function (validating a certificate without an SSL connection)
  # does not seem to have many equivalents at all in python. OpenSSL module
  # seems to be a rare implementation of it, so we keep using this module.
  # BUT it MUST NOT be used anywhere outside this function (hence the
  # bad-style local import). Use "cryptography".
  from OpenSSL import crypto
  store = crypto.X509Store()
  assert trusted_cert_list
  for trusted_cert in trusted_cert_list:
    store.add_cert(crypto.X509.from_cryptography(trusted_cert))
  if crl is not None:
    store.add_crl(crypto.CRL.from_cryptography(crl))
    store.set_flags(crypto.X509StoreFlags.CRL_CHECK)
  try:
    crypto.X509StoreContext(
      store,
      crypto.X509.from_cryptography(cert),
    ).verify_certificate()
  except (
    crypto.X509StoreContextError,
    crypto.Error,
  ), e:
    raise CertificateVerificationError(
      'Certificate verification error: %s' % str(e),
    )

def wrap(payload, key, digest):
  """
  Sign payload (which gets json-serialised) with key, using given digest.
  """
  payload = json.dumps(payload).encode('utf-8')
  hash_class = getattr(hashes, digest.upper())
  return {
    'payload': payload,
    'digest': digest,
    'signature': key.sign(
      payload + digest + ' ',
      padding.PSS(
        mgf=padding.MGF1(hash_class()),
        salt_length=padding.PSS.MAX_LENGTH,
      ),
      hash_class(),
    ).encode('base64'),
  }

def nullWrap(payload):
  """
  Wrap without signature. To only be used (and accepted) when user is
  authenticated (and hence using a secure channel, HTTPS).
  """
  return {
    'payload': json.dumps(payload),
    'digest': None,
  }

def unwrap(wrapped, getCertificate, digest_list):
  """
  Check payload signature and return it.

  Raises cryptography.exceptions.InvalidSignature if signature does not match
  payload or if transmitted digest is not an acceptable one.

  Note: does *not* verify received certificate itself (validity, issuer, ...).
  """
  # Check whether given digest is allowed
  digest = wrapped['digest'].encode('ascii')
  if digest not in digest_list:
    raise cryptography.exceptions.UnsupportedAlgorithm(
      '%r is not in allowed digest list',
    )
  hash_class = getattr(hashes, digest.upper())
  try:
    payload = json.loads(wrapped['payload'])
  except ValueError:
    raise NotJSON
  x509.load_pem_x509_certificate(
    getCertificate(payload).encode('ascii'),
    _cryptography_backend,
  ).public_key().verify(
    wrapped['signature'].encode('ascii').decode('base64'),
    wrapped['payload'].encode('utf-8') + digest + ' ',
    padding.PSS(
      mgf=padding.MGF1(hash_class()),
      salt_length=padding.PSS.MAX_LENGTH,
    ),
    hash_class(),
  )
  return payload

def nullUnwrap(wrapped):
  """
  Un-wrapp unsigned content. To onl be used on content received from
  an authenticated user (and hence over a secure channel, HTTPS).
  """
  assert wrapped['digest'] is None
  try:
    return json.loads(wrapped['payload'])
  except ValueError:
    raise NotJSON

def load_ca_certificate(data):
  """
  Load CA certificate from PEM-encoded data.

  Raises CertificateVerificationError if loaded certificate is not self-signed
  or is otherwise invalid.
  """
  crt = x509.load_pem_x509_certificate(data, _cryptography_backend)
  _verifyCertificateChain(crt, [crt], None)
  return crt

def load_certificate(data, trusted_cert_list, crl):
  """
  Load a certificate from PEM-encoded data.

  Raises CertificateVerificationError if loaded certificate is not signed by
  any of trusted certificates, is revoked or is otherwise invalid.
  """
  crt = x509.load_pem_x509_certificate(data, _cryptography_backend)
  _verifyCertificateChain(crt, trusted_cert_list, crl)
  return crt

def dump_certificate(data):
  """
  Serialise a certificate as PEM-encoded data.
  """
  return data.public_bytes(serialization.Encoding.PEM)

def load_certificate_request(data):
  """
  Load a certificate request from PEM-encoded data.

  Raises cryptography.exceptions.InvalidSignature if certificate signature
  does not match embedded public key.
  """
  result = x509.load_pem_x509_csr(data, _cryptography_backend)
  if not result.is_signature_valid:
    raise cryptography.exceptions.InvalidSignature
  return result

def dump_certificate_request(data):
  """
  Serialise acertificate request as PEM-encoded data.
  """
  return data.public_bytes(
    encoding=serialization.Encoding.PEM,
  )

def load_privatekey(data):
  """
  Load a private key from PEM-encoded data.
  """
  return serialization.load_pem_private_key(
    data,
    password=None,
    backend=_cryptography_backend,
  )

def dump_privatekey(data):
  """
  Serialise a private key as PEM-encoded data.
  """
  return data.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption(),
  )

def generatePrivateKey(key_len):
  """
  Generate a new private key of specified length.
  """
  return rsa.generate_private_key(
    public_exponent=65537,
    key_size=key_len,
    backend=_cryptography_backend,
  )

def load_crl(data, trusted_cert_list):
  """
  Load a certificate revocation list from PEM-encoded data.

  If cryptography supports it, raises cryptography.exceptions.InvalidSignature
  if the CRL signature does not match any trusted certificate.
  """
  crl = x509.load_pem_x509_crl(data, _cryptography_backend)
  for cert in trusted_cert_list:
    if crl.is_signature_valid(cert.public_key()):
      return crl
  raise cryptography.exceptions.InvalidSignature

EPOCH = datetime.datetime(1970, 1, 1)
def datetime2timestamp(value):
  """
  Convert given datetime into a unix timestamp.
  """
  return (value - EPOCH).total_seconds()

class SleepInterrupt(KeyboardInterrupt):
  """
  A sleep was interrupted by a KeyboardInterrupt
  """
  pass

def interruptibleSleep(duration): # pragma: no cover
  """
  Like sleep, but raises SleepInterrupt when interrupted by KeyboardInterrupt
  """
  try:
    time.sleep(duration)
  except KeyboardInterrupt:
    raise SleepInterrupt

def until(deadline): # pragma: no cover
  """
  Call interruptibleSleep until deadline is reached.
  """
  now = datetime.datetime.utcnow()
  while now < deadline:
    interruptibleSleep((deadline - now).total_seconds())
    now = datetime.datetime.utcnow()
  return now
