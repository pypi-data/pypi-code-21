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
"""
from __future__ import absolute_import
import datetime
import json
import os
import struct
import threading
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes, hmac
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.padding import OAEP, MGF1
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from . import utils
from .exceptions import (
  CertificateVerificationError,
  NotACertificateSigningRequest,
)

__all__ = ('CertificateAuthority', )

_cryptography_backend = default_backend()
_AUTO_SIGNED_NO = 0
_AUTO_SIGNED_YES = 1
_AUTO_SIGNED_PASSTHROUGH = 2
_SUBJECT_OID_DICT = {
  # pylint: disable=bad-whitespace
  'C' : x509.oid.NameOID.COUNTRY_NAME,
  'O' : x509.oid.NameOID.ORGANIZATION_NAME,
  'OU': x509.oid.NameOID.ORGANIZATIONAL_UNIT_NAME,
  'ST': x509.oid.NameOID.STATE_OR_PROVINCE_NAME,
  'CN': x509.oid.NameOID.COMMON_NAME,
  'L' : x509.oid.NameOID.LOCALITY_NAME,
  'SN': x509.oid.NameOID.SURNAME,
  'GN': x509.oid.NameOID.GIVEN_NAME,
  # pylint: enable=bad-whitespace
}
_BACKUP_MAGIC = 'caucase\0'
_CONFIG_NAME_AUTO_SIGN_CSR_AMOUNT = 'auto_sign_csr_amount'

def Extension(value, critical):
  """
  Avoid oid redundant parameter when creating an extension.
  """
  return x509.Extension(
    oid=value.oid,
    critical=critical,
    value=value,
  )

class CertificateAuthority(object):
  """
  This class implements CA policy and lifetime logic:
  - how CA key pair is generated
  - what x509.3 extensions and attributes are enforced on signed certificates
  - CA and CRL automated renewal
  """
  def __init__(
    self,
    storage,
    ca_subject_dict=(),
    ca_key_size=2048,
    crt_life_time=31 * 3, # Approximately 3 months
    ca_life_period=4, # Approximately a year
    crl_renew_period=0.33, # Approximately a month
    crl_base_url=None,
    digest_list=utils.DEFAULT_DIGEST_LIST,
    auto_sign_csr_amount=0,
    lock_auto_sign_csr_amount=False,
  ):
    """
    storage (caucase.storage.Storage)
      Persistent storage of certificate authority data.

    ca_subject_dict (dict)
      Items to use as Certificate Authority certificate subject.
      Supported keys are: C, O, OU, ST, CN, L, SN, GN.

    ca_key_size (int, None)
      Number of bits to use as Certificate Authority key.
      None to disable CA renewal.

    crt_life_time (float)
      Validity duration for every issued certificate, in days.

    ca_life_period (float)
      Number of crt_life_time periods for which Certificate Authority
      certificate will be valid.
      Must be greater than 3 to allow smooth rollout.

    crl_renew_period (float)
      Number of crt_life_time periods for which a revocation list is
      valid for.

    crl_base_url (str)
      The CRL distribution URL to include in signed certificates.
      None to not declare a CRL distribution point in generated certificates.
      Revocations are be functional even if this is None.

    digest_list (list of str)
      List of digest algorithms considered acceptable for authenticating
      renewal and revocation requests, and CA renewal list responses.
      The first item will be the one used, others are accepted but not used.

    auto_sign_csr_amount (int)
      Automatically sign the first <auto_sign_csr_amount> CSRs.
      As certificate gets unconditionally emitted and only vital attributes
      and extensions are forced during signature, you should choose the
      smallest amount possible to get a functional service.
      For a typical HTTP(S) caucase service, 1 should be enough for CAS usage
      (first service certificate being to serve HTTPS for caucase), and 1 for
      CAU usage (first user, which can then sign more user certificate
      requests).
      To verify nothing accessed the service before intended automated
      requests, check issued certificate has an extension with OID:
        2.25.285541874270823339875695650038637483517.0
      (a message is printed when retrieving the certificate)
      This mark is propagated during certificate renewal.

    lock_auto_sign_csr_amount (bool)
      When given with a true value, auto_sign_csr_amount is stored and the
      value given on later instanciation will be ignored.
    """
    self._storage = storage
    self._ca_renewal_lock = threading.Lock()
    if lock_auto_sign_csr_amount:
      storage.setConfigOnce(
        _CONFIG_NAME_AUTO_SIGN_CSR_AMOUNT,
        auto_sign_csr_amount,
      )
    self._auto_sign_csr_amount = int(storage.getConfigOnce(
      _CONFIG_NAME_AUTO_SIGN_CSR_AMOUNT,
      auto_sign_csr_amount,
    ))

    self._ca_key_size = ca_key_size
    self._digest_list = digest_list
    self._default_digest_class = getattr(hashes, self.digest_list[0].upper())
    self._crt_life_time = datetime.timedelta(crt_life_time, 0)
    self._crl_base_url = crl_base_url
    self._ca_subject = x509.Name([
      x509.NameAttribute(
        oid=_SUBJECT_OID_DICT[key],
        value=value,
      )
      for key, value in dict(ca_subject_dict).iteritems()
    ])
    if ca_life_period < 3:
      raise ValueError("ca_life_period must be >= 3 to allow CA rollout")
    self._crl_life_time = datetime.timedelta(
      crt_life_time * crl_renew_period,
      0,
    )
    self._ca_life_time = datetime.timedelta(crt_life_time * ca_life_period, 0)
    self._loadCAKeyPairList()
    self._renewCAIfNeeded()

  @property
  def digest_list(self):
    """
    Read-only access to digest_list ctor parameter.
    """
    return list(self._digest_list)

  def _loadCAKeyPairList(self):
    ca_key_pair_list = []
    for pem_key_pair in self._storage.getCAKeyPairList():
      utils.validateCertAndKey(
        pem_key_pair['crt_pem'],
        pem_key_pair['key_pem'],
      )
      ca_key_pair_list.append({
        'crt': utils.load_ca_certificate(pem_key_pair['crt_pem']),
        'key': utils.load_privatekey(pem_key_pair['key_pem']),
      })
    self._ca_key_pairs_list = ca_key_pair_list

  def getCertificateSigningRequest(self, csr_id):
    """
    Retrieve a PEM-encoded certificate signing request.

    csr_id (int)
      As returned when the CSR was stored.
    """
    return self._storage.getCertificateSigningRequest(csr_id)

  def appendCertificateSigningRequest(self, csr_pem, override_limits=False):
    """
    Store certificate signing request and return its identifier.
    May trigger its signature if the quantity of submitted CSRs is less than
    auto_sign_csr_amount (see __init__).

    csr_pem (str)
      PEM-encoded certificate signing request.
    """
    try:
      csr = utils.load_certificate_request(csr_pem)
    except ValueError:
      raise NotACertificateSigningRequest
    # Note: requested_amount is None when a known CSR is re-submitted
    csr_id, requested_amount = self._storage.appendCertificateSigningRequest(
      csr_pem=csr_pem,
      key_id=x509.SubjectKeyIdentifier.from_public_key(
        csr.public_key(),
      ).digest.encode('hex'),
      override_limits=override_limits,
    )
    if requested_amount is not None and \
    requested_amount <= self._auto_sign_csr_amount:
      # if allowed to sign this certificate automaticaly
      self._createCertificate(csr_id, auto_signed=_AUTO_SIGNED_YES)
    return csr_id

  def deletePendingCertificateSigningRequest(self, csr_id):
    """
    Reject a pending certificate signing request.

    csr_id (int)
      CSR id, as returned when the CSR was stored.
    """
    self._storage.deletePendingCertificateSigningRequest(csr_id)

  def getCertificateRequestList(self):
    """
    Return the list of pending certificate signature requests, individually
    PEM-encoded.
    """
    return self._storage.getCertificateSigningRequestList()

  def createCertificate(self, csr_id, template_csr=None):
    """
    Sign a pending certificate signing request, storing produced certificate.

    csr_id (int)
      CSR id, as returned when the CSR was stored.
    template_csr (None or X509Req)
      Copy extensions and subject from this CSR instead of stored one.
      Useful to renew a certificate.
      Public key is always copied from stored CSR.
    """
    self._createCertificate(
      csr_id=csr_id,
      auto_signed=_AUTO_SIGNED_NO,
      template_csr=template_csr,
    )

  def _createCertificate(self, csr_id, auto_signed, template_csr=None):
    """
    auto_signed (bool)
      When True, mark certificate as having been auto-signed.
      When False, prevent such mark from being set.
      When None, do not filter (useful when renewing).
    tempate_csr (None or X509Req)
      Copy extensions and subject from this CSR instead of stored one.
      Useful to renew a certificate.
      Public key is always copied from stored CSR.
    """
    csr_pem = self._storage.getCertificateSigningRequest(csr_id)
    csr = utils.load_certificate_request(csr_pem)
    if template_csr is None:
      template_csr = csr
    ca_key_pair = self._getCurrentCAKeypair()
    ca_crt = ca_key_pair['crt']

    public_key = csr.public_key()
    subject_key_identifier = x509.SubjectKeyIdentifier.from_public_key(
      public_key,
    )
    now = datetime.datetime.utcnow()
    builder = x509.CertificateBuilder(
      subject_name=template_csr.subject,
      issuer_name=ca_crt.subject,
      not_valid_before=now,
      not_valid_after=now + self._crt_life_time,
      serial_number=x509.random_serial_number(),
      public_key=public_key,
      extensions=[
        Extension(
          x509.BasicConstraints(
            ca=False,
            path_length=None,
          ),
          critical=True, # "MAY appear as critical or non-critical"
        ),
        Extension(
          subject_key_identifier,
          critical=False, # "MUST mark this extension as non-critical"
        ),
        Extension(
          x509.AuthorityKeyIdentifier.from_issuer_subject_key_identifier(
            ca_crt.extensions.get_extension_for_class(
              x509.SubjectKeyIdentifier,
            ),
          ),
          critical=False, # "MUST mark this extension as non-critical"
        ),
      ],
    )
    if self._crl_base_url:
      builder = builder.add_extension(
        x509.CRLDistributionPoints([
          x509.DistributionPoint(
            full_name=[
              x509.UniformResourceIdentifier(self._crl_base_url),
            ],
            relative_name=None,
            crl_issuer=None,
            reasons=None,
          ),
        ]),
        critical=False, # "SHOULD be non-critical"
      )
    try:
      key_usage_extension = template_csr.extensions.get_extension_for_class(
        x509.KeyUsage,
      )
    except x509.ExtensionNotFound:
      pass
    else:
      key_usage = key_usage_extension.value
      if key_usage.key_agreement:
        encipher_only = key_usage.encipher_only
        decipher_only = key_usage.decipher_only
      else:
        encipher_only = decipher_only = False
      builder = builder.add_extension(
        x509.KeyUsage(
          # pylint: disable=bad-whitespace
          digital_signature =key_usage.digital_signature,
          content_commitment=key_usage.content_commitment,
          key_encipherment  =key_usage.key_encipherment,
          data_encipherment =key_usage.data_encipherment,
          key_agreement     =key_usage.key_agreement,
          key_cert_sign     =False,
          crl_sign          =False,
          encipher_only     =encipher_only,
          decipher_only     =decipher_only,
          # pylint: enable=bad-whitespace
        ),
        # "SHOULD mark this extension critical"
        critical=key_usage_extension.critical,
      )
    try:
      extended_key_usage = template_csr.extensions.get_extension_for_class(
        x509.ExtendedKeyUsage,
      )
    except x509.ExtensionNotFound:
      pass
    else:
      builder = builder.add_extension(
        x509.ExtendedKeyUsage(
          [
            x for x in extended_key_usage.value
            if x != x509.oid.ExtendedKeyUsageOID.OCSP_SIGNING
          ]
        ),
        critical=extended_key_usage.critical,
      )
    try:
      subject_alt_name = template_csr.extensions.get_extension_for_class(
        x509.SubjectAlternativeName,
      )
    except x509.ExtensionNotFound:
      pass
    else:
      # Note: as issued certificates may be used without any subject
      # validation (ex: connecting to mariadb via a variable IP), we
      # voluntarily do not enforce any constraint on subjectAltName.
      builder = builder.add_extension(
        subject_alt_name.value,
        critical=subject_alt_name.critical,
      )
    # subjectDirectoryAttributes ?
    try:
      certificate_policies = template_csr.extensions.get_extension_for_class(
        x509.CertificatePolicies,
      )
    except x509.ExtensionNotFound:
      if auto_signed == _AUTO_SIGNED_YES:
        builder = builder.add_extension(
          x509.CertificatePolicies([
            utils.CAUCASE_POLICY_INFORMATION_AUTO_SIGNED,
          ]),
          critical=False, # (no recommendations)
        )
    else:
      if auto_signed == _AUTO_SIGNED_PASSTHROUGH:
        # Caller is asking us to let all through, so do this.
        policy_list = certificate_policies.value
      else:
        # Prevent any caucase extension from being smuggled, especiall the
        # "auto-signed" one...
        policy_list = [
          x for x in certificate_policies.value
          if not x.policy_identifier.dotted_string.startswith(
            utils.CAUCASE_OID_TOP,
          )
        ]
        if auto_signed == _AUTO_SIGNED_YES:
          # ...but do add auto-signed extension if we are auto-signing.
          policy_list.append(utils.CAUCASE_POLICY_INFORMATION_AUTO_SIGNED)
      builder = builder.add_extension(
        x509.CertificatePolicies(policy_list),
        critical=certificate_policies.critical, # (no recommendations)
      )

    cert_pem = utils.dump_certificate(builder.sign(
      private_key=ca_key_pair['key'],
      algorithm=self._default_digest_class(),
      backend=_cryptography_backend,
    ))
    self._storage.storeCertificate(csr_id, cert_pem)
    return cert_pem

  def getCertificate(self, csr_id):
    """
    Return PEM-encoded signed certificate.

    csr_id (int)
      As returned when the corresponding CSR was stored.
    """
    return self._storage.getCertificate(csr_id)

  def _renewCAIfNeeded(self):
    """
    Create a new CA certificate if latest one has less than two
    ca_life_periods of validity left.
    Updates self._ca_key_pairs_list .
    """
    if (
      self._ca_key_size is not None and not self._ca_key_pairs_list or (
        self._ca_key_pairs_list[-1]['crt'].not_valid_after -
        datetime.datetime.utcnow()
      ).total_seconds() / self._crt_life_time.total_seconds() <= 2
    ) and self._ca_renewal_lock.acquire(False):
      try:
        # No CA certificate at all or less than 2 certificate validity periods
        # left with latest CA certificate. Prepare the next one so it starts
        # getting distributed.
        private_key = rsa.generate_private_key(
          public_exponent=65537,
          key_size=self._ca_key_size,
          backend=_cryptography_backend,
        )
        if self._ca_key_pairs_list:
          latest_crt = self._ca_key_pairs_list[-1]['crt']
          subject = latest_crt.subject
          extension_list = latest_crt.extensions
        else:
          # Provide a default subject extension set.
          subject = self._ca_subject
          extension_list = [
            Extension(
              x509.BasicConstraints(
                ca=True,
                path_length=0,
              ),
              critical=True, # "MUST mark the extension as critical"
            ),
            Extension(
              x509.KeyUsage(
                # pylint: disable=bad-whitespace
                digital_signature =False,
                content_commitment=False,
                key_encipherment  =False,
                data_encipherment =False,
                key_agreement     =False,
                key_cert_sign     =True,
                crl_sign          =True,
                encipher_only     =False,
                decipher_only     =False,
                # pylint: enable=bad-whitespace
              ),
              critical=True, # "SHOULD mark this extension critical"
            ),
# Should we make use of certificate policies ? If we do, we need to enable
# this extension and fill the values.
#            Extension(
#              x509.PolicyConstraints(
#                require_explicit_policy=,
#                inhibit_policy_mapping=,
#              ),
#              critical=True, # MUST mark this extension as critical
#            ),
          ]
        public_key = private_key.public_key()
        subject_key_identifier = x509.SubjectKeyIdentifier.from_public_key(
          public_key,
        )
        now = datetime.datetime.utcnow()
        crt_builder = x509.CertificateBuilder(
          subject_name=subject,
          issuer_name=subject,
          not_valid_before=now,
          not_valid_after=now + self._ca_life_time,
          serial_number=x509.random_serial_number(),
          public_key=public_key,
          extensions=[
            Extension(
              subject_key_identifier,
              critical=False, # "MUST mark this extension as non-critical"
            ),
            Extension(
              x509.AuthorityKeyIdentifier.from_issuer_subject_key_identifier(
                # Dummy extension, from_issuer_subject_key_identifier accesses
                # .data directly
                Extension(
                  subject_key_identifier,
                  critical=False,
                ),
              ),
              critical=False, # "MUST mark this extension as non-critical"
            ),
          ],
        )
        # Copy all extensions, except the ones which depend on the key (and
        # which we just set).
        skipped_extension_oid_set = (
          x509.SubjectKeyIdentifier.oid,
          x509.AuthorityKeyIdentifier.oid,
        )
        for extension in extension_list:
          if extension.oid not in skipped_extension_oid_set:
            crt_builder = crt_builder.add_extension(
              extension.value,
              extension.critical,
            )
        certificate = crt_builder.sign(
          private_key=private_key,
          algorithm=self._default_digest_class(),
          backend=_cryptography_backend,
        )
        self._storage.appendCAKeyPair(
          utils.datetime2timestamp(certificate.not_valid_after),
          {
            'key_pem': utils.dump_privatekey(private_key),
            'crt_pem': utils.dump_certificate(certificate),
          },
        )
        self._loadCAKeyPairList()
        assert self._ca_key_pairs_list
      finally:
        self._ca_renewal_lock.release()

  def _getCurrentCAKeypair(self):
    """
    Return the currently-active CA certificate key pair.

    Currently-active CA certificate is the CA to use when signing. It may not
    be the latest one, as all certificate holders must know the latest one
    before its use can start.
    """
    self._renewCAIfNeeded()
    now = datetime.datetime.utcnow()
    for key_pair in reversed(self._ca_key_pairs_list):
      if key_pair['crt'].not_valid_before + self._crt_life_time < now:
        # This CA cert is valid for more than one certificate life time,
        # we can assume clients to know it (as they had to renew their
        # cert at least once since it became available) so we can start
        # using it.
        break
    else:
      # No CA cert is valid for more than one certificate life time, so just
      # pick the newest one.
      key_pair = self._ca_key_pairs_list[-1]
    return key_pair

  def getCACertificate(self):
    """
    Return current CA certificate, PEM-encoded.
    """
    return utils.dump_certificate(self._getCurrentCAKeypair()['crt'])

  def getCACertificateList(self):
    """
    Return the current list of CA certificates as X509 obbjects.
    """
    self._renewCAIfNeeded()
    return [x['crt'] for x in self._ca_key_pairs_list]

  def getValidCACertificateChain(self):
    """
    Return the CA certificate chain based on oldest CA certificate.

    Each item in the chain is a wrapped dict with the following keys:
    old (str)
      N-1 certificate as PEM, used to check wrapper signature.
      If item is the first in the chain, this is the oldest CA certificate
      server still knows about.
    new (str)
      N certificate as PEM.

    The intent is for a client knowing one CA certificate to retrieve any newer
    CA certificate and autonomously decide if it may trust them: each item is
    signed with the previous certificate. The oldest CA certificate is not
    returned in this list, as it cannot be signed by another one.

    CA user must check that there is an uninterrupted signed path from its
    already-known CA certificate to use any contained "new" certificate.
    It must skip any certificate pair for which it does not already trust
    an ancestor certificate.

    Note: the chain may contain expired CA certificates. CA user should skip
    these, and consider their signature invalid for CA chain validation
    purposes.
    """
    self._renewCAIfNeeded()
    result = []
    iter_key_pair = iter(self._ca_key_pairs_list)
    first_key_pair = iter_key_pair.next()
    previous_crt_pem = utils.dump_certificate(first_key_pair['crt'])
    previous_key = first_key_pair['key']
    for key_pair in iter_key_pair:
      current_crt_pem = utils.dump_certificate(key_pair['crt'])
      result.append(utils.wrap(
        {
          'old_pem': previous_crt_pem,
          'new_pem': current_crt_pem,
        },
        previous_key,
        self.digest_list[0],
      ))
      previous_key = key_pair['key']
      previous_crt_pem = current_crt_pem
    return result

  def revoke(self, crt_pem):
    """
    Revoke certificate.

    crt_pem (str)
      PEM-encoded certificat to revoke.
    """
    crt = utils.load_certificate(
      crt_pem,
      self.getCACertificateList(),
      x509.load_pem_x509_crl(
        self.getCertificateRevocationList(),
        _cryptography_backend,
      ),
    )
    self._storage.revoke(
      serial=crt.serial_number,
      expiration_date=utils.datetime2timestamp(crt.not_valid_after),
    )

  def revokeSerial(self, serial):
    """
    Revoke a certificate by its serial only.

    Revocation will expire when the latest CA certificate of this instance
    expires, meaning it will stay longer in the revocation list than when
    certificate expiration date can be retrieved from the certificate.

    Also, there cannot be any check on the validity of the serial, typos
    are accepted verbatim.

    Using this method is hence not recomended.
    """
    self._storage.revoke(
      serial=serial,
      expiration_date=utils.datetime2timestamp(max(
        x.not_valid_after for x in self.getCACertificateList()
      )),
    )

  def renew(self, crt_pem, csr_pem):
    """
    Renew certificate.

    crt_pem (str)
      PEM-encoded certificate to renew.
    csr_pem (str)
      PEM-encoded certificate signing request.
    """
    ca_cert_list = self.getCACertificateList()
    crt = utils.load_certificate(
      crt_pem,
      ca_cert_list,
      x509.load_pem_x509_crl(
        self.getCertificateRevocationList(),
        _cryptography_backend,
      ),
    )
    return self._createCertificate(
      csr_id=self.appendCertificateSigningRequest(
        csr_pem,
        override_limits=True,
      ),
      auto_signed=_AUTO_SIGNED_PASSTHROUGH,
      # Do a dummy signature, just so we get a usable
      # x509.CertificateSigningRequest instance. Use latest CA private key just
      # because it is available for free (unlike generating a new one).
      template_csr=x509.CertificateSigningRequestBuilder(
        subject_name=crt.subject,
        extensions=crt.extensions,
      ).sign(
        private_key=self._ca_key_pairs_list[-1]['key'],
        algorithm=self._default_digest_class(),
        backend=_cryptography_backend,
      ),
    )

  def getCertificateRevocationList(self):
    """
    Return PEM-encoded certificate revocation list.
    """
    crl_pem = self._storage.getCertificateRevocationList()
    if crl_pem is None:
      ca_key_pair = self._getCurrentCAKeypair()
      now = datetime.datetime.utcnow()
      crl = x509.CertificateRevocationListBuilder(
        issuer_name=ca_key_pair['crt'].issuer,
        last_update=now,
        next_update=now + self._crl_life_time,
        extensions=[
          Extension(
            x509.CRLNumber(
              self._storage.getNextCertificateRevocationListNumber(),
            ),
            critical=False, # "MUST mark this extension as non-critical"
          ),
        ],
        revoked_certificates=[
          x509.RevokedCertificateBuilder(
            serial_number=x['serial'],
            revocation_date=datetime.datetime.fromtimestamp(
              x['revocation_date'],
            ),
          ).build(_cryptography_backend)
          for x in self._storage.getRevocationList()
        ],
      ).sign(
        private_key=ca_key_pair['key'],
        algorithm=self._default_digest_class(),
        backend=_cryptography_backend,
      )
      crl_pem = crl.public_bytes(serialization.Encoding.PEM)
      self._storage.storeCertificateRevocationList(
        crl_pem,
        expiration_date=utils.datetime2timestamp(crl.next_update),
      )
    return crl_pem

class UserCertificateAuthority(CertificateAuthority):
  """
  Backup-able CertificateAuthority.

  See backup schema in documentation.
  """

  def doBackup(self, write):
    """
    Backup the entire storage to given path, enciphering it using all stored
    certificates.
    """
    ca_cert_list = self.getCACertificateList()
    crl = x509.load_pem_x509_crl(
      self.getCertificateRevocationList(),
      _cryptography_backend,
    )
    signing_key = os.urandom(32)
    symetric_key = os.urandom(32)
    iv = os.urandom(16)
    encryptor = Cipher(
      algorithms.AES(symetric_key),
      modes.CBC(iv),
      backend=_cryptography_backend,
    ).encryptor()
    authenticator = hmac.HMAC(
      signing_key,
      hashes.SHA256(),
      backend=_cryptography_backend,
    )
    HMAC_PAYLOAD_SIZE = 10 * 1024 * 1024
    key_list = []
    for crt_pem in self._storage.iterCertificates():
      try:
        crt = utils.load_certificate(crt_pem, ca_cert_list, crl)
      except CertificateVerificationError:
        continue
      public_key = crt.public_key()
      key_list.append({
        'id': x509.SubjectKeyIdentifier.from_public_key(
          public_key,
        ).digest.encode('hex'),
        'cipher': {
          'name': 'rsa_oaep_sha1_mgf1_sha1',
        },
        'key': public_key.encrypt(
          signing_key + symetric_key,
          OAEP(
            mgf=MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(),
            label=None,
          ),
        ).encode('hex'),
      })
    if not key_list:
      # No users yet, backup is meaningless
      return False
    header = json.dumps({
      'cipher': {
        'name': 'aes256_cbc_pkcs7_hmac_10M_sha256',
        'parameter': iv.encode('hex'),
      },
      'key_list': key_list,
    })
    padder = padding.PKCS7(128).padder()
    write(_BACKUP_MAGIC)
    write(struct.pack('<I', len(header)))
    write(header)
    def signingIterator():
      """
      Iterate over cleartext dump, inserting HMAC between each chunk.
      """
      buf = b''
      for chunk in self._storage.dumpIterator():
        buf += chunk
        while len(buf) >= HMAC_PAYLOAD_SIZE:
          chunk = buf[:HMAC_PAYLOAD_SIZE]
          buf = buf[HMAC_PAYLOAD_SIZE:]
          authenticator.update(chunk)
          yield chunk
          yield authenticator.copy().finalize()
      if buf:
        authenticator.update(buf)
        yield buf
        yield authenticator.finalize()
    for chunk in signingIterator():
      write(encryptor.update(padder.update(chunk)))
    write(encryptor.update(padder.finalize()))
    write(encryptor.finalize())
    return True

  @classmethod
  def restoreBackup(
    cls,
    db_class,
    db_path,
    read,
    key_pem,
    csr_pem,
    db_kw=(),
    kw=(),
  ):
    """
    Restore backup, revoke certificate corresponding to private key and sign
    its renewal.
    """
    magic = read(8)
    if magic != _BACKUP_MAGIC:
      raise ValueError('Invalid backup magic string')
    header_len, = struct.unpack(
      '<I',
      read(struct.calcsize('<I')),
    )
    header = json.loads(read(header_len))
    if header['cipher']['name'] != 'aes256_cbc_pkcs7_hmac_10M_sha256':
      raise ValueError('Unrecognised symetric cipher')
    private_key = utils.load_privatekey(key_pem)
    key_id = x509.SubjectKeyIdentifier.from_public_key(
      private_key.public_key(),
    ).digest.encode('hex')
    symetric_key_list = [
      x for x in header['key_list'] if x['id'] == key_id
    ]
    if not symetric_key_list:
      raise ValueError(
        'Given private key is not a good candidate for restoring this backup',
      )
    symetric_key_entry, = symetric_key_list
    if symetric_key_entry['cipher']['name'] != 'rsa_oaep_sha1_mgf1_sha1':
      raise ValueError('Unrecognised asymetric cipher')
    both_keys = private_key.decrypt(
      symetric_key_entry['key'].decode('hex'),
      OAEP(
        mgf=MGF1(algorithm=hashes.SHA1()),
        algorithm=hashes.SHA1(),
        label=None,
      ),
    )
    if len(both_keys) != 64:
      raise ValueError('Invalid key length')
    decryptor = Cipher(
      algorithms.AES(both_keys[32:]),
      modes.CBC(header['cipher']['parameter'].decode('hex')),
      backend=_cryptography_backend,
    ).decryptor()
    unpadder = padding.PKCS7(128).unpadder()
    authenticator = hmac.HMAC(
      both_keys[:32],
      hashes.SHA256(),
      backend=_cryptography_backend,
    )
    HMAC_PAYLOAD_SIZE = 10 * 1024 * 1024
    # Each block has its signature
    HMAC_SIGNED_SIZE = HMAC_PAYLOAD_SIZE + 32
    CHUNK_SIZE = HMAC_SIGNED_SIZE
    def restorator():
      """
      Iterate over backup payload, decyphering by small chunks.
      """
      while True:
        chunk = read(CHUNK_SIZE)
        if chunk:
          yield unpadder.update(decryptor.update(chunk))
        else:
          yield unpadder.update(decryptor.finalize()) + unpadder.finalize()
          break
    def verificator():
      """
      Iterate over decrypted payload, verifying HMAC on each chunk.
      """
      buf = b''
      for clear in restorator():
        buf += clear
        while len(buf) >= HMAC_SIGNED_SIZE:
          signed = buf[:HMAC_SIGNED_SIZE]
          buf = buf[HMAC_SIGNED_SIZE:]
          chunk = signed[:-32]
          authenticator.update(chunk)
          authenticator.copy().verify(signed[-32:])
          yield chunk
      if buf:
        chunk = buf[:-32]
        authenticator.update(chunk)
        authenticator.verify(buf[-32:])
        yield chunk

    db_class.restore(db_path=db_path, restorator=verificator())

    # Now that the database is restored, use a CertificateAuthority to
    # renew & revoke given private key.
    self = cls(storage=db_class(db_path=db_path, **dict(db_kw)), **dict(kw))
    # pylint: disable=protected-access
    crt_pem = self._storage.getCertificateByKeyIdentifier(key_id)
    # pylint: enable=protected-access
    new_crt_pem = self.renew(crt_pem, csr_pem)
    self.revoke(crt_pem)
    return new_crt_pem
