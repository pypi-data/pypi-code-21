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
import httplib
import json
import os
import ssl
from urlparse import urlparse
from cryptography import x509
from cryptography.hazmat.backends import default_backend
import cryptography.exceptions
from . import utils

__all__ = (
  'CaucaseError',
  'CaucaseClient',
  'HTTPSOnlyCaucaseClient',
  'updateCAFile',
  'updateCRLFile',
)

_cryptography_backend = default_backend()

class CaucaseError(Exception):
  """
  Raised when server responds with an HTTP error status.
  """
  pass

def updateCAFile(url, ca_crt_path):
  """
  Bootstrap anf maintain a CA file up-to-date.

  url (str)
    URL to caucase, ending in eithr /cas or /cau.
  ca_crt_path (str)
    Path to the CA certificate file, which may not exist.

  Return whether an update happened (including whether an already-known
  certificate expired and was discarded).
  """
  if not os.path.exists(ca_crt_path):
    ca_pem = CaucaseClient(
      ca_url=url,
    ).getCACertificate()
    with open(ca_crt_path, 'w') as ca_crt_file:
      ca_crt_file.write(ca_pem)
    updated = True
  else:
    updated = False
  now = datetime.datetime.utcnow()
  loaded_ca_pem_list = utils.getCertList(ca_crt_path)
  ca_pem_list = [
    x
    for x in loaded_ca_pem_list
    if utils.load_ca_certificate(x).not_valid_after > now
  ]
  ca_pem_list.extend(
    CaucaseClient(
      ca_url=url,
      ca_crt_pem_list=ca_pem_list,
    ).getCACertificateChain(),
  )
  if ca_pem_list != loaded_ca_pem_list:
    data = ''.join(ca_pem_list)
    with open(ca_crt_path, 'w') as ca_crt_file:
      ca_crt_file.write(data)
    updated = True
  return updated

def updateCRLFile(url, crl_path, ca_list):
  """
  Bootstrap anf maintain a CRL file up-to-date.

  url (str)
    URL to caucase, ending in eithr /cas or /cau.
  crl_path (str)
    Path to the CRL file, which may not exist.
  ca_list (list of cryptography.x509.Certificate instances)
    One of these CA certificates must have signed the CRL for it to be
    accepted.

  Return whether an update happened.
  """
  if os.path.exists(crl_path):
    my_crl = utils.load_crl(open(crl_path).read(), ca_list)
  else:
    my_crl = None
  latest_crl_pem = CaucaseClient(
    ca_url=url,
  ).getCertificateRevocationList()
  latest_crl = utils.load_crl(latest_crl_pem, ca_list)
  if my_crl is None or latest_crl.signature != my_crl.signature:
    with open(crl_path, 'w') as crl_file:
      crl_file.write(latest_crl_pem)
    return True
  return False

class CaucaseClient(object):
  """
  Caucase HTTP(S) client.

  Expose caucase REST API as pythonic methods.
  """
  def __init__(self, ca_url, ca_crt_pem_list=None, user_key=None):
    # XXX: set timeout to HTTP connections ?
    http_url = urlparse(ca_url)
    port = http_url.port or 80
    self._http_connection = httplib.HTTPConnection(
      http_url.hostname,
      port,
      #timeout=,
    )
    self._ca_crt_pem_list = ca_crt_pem_list
    self._path = http_url.path
    if ca_crt_pem_list:
      ssl_context = ssl.create_default_context(
        # unicode object needed as we use PEM, otherwise create_default_context
        # expects DER.
        cadata=''.join(ca_crt_pem_list).decode('ascii'),
      )
      if user_key:
        ssl_context.load_cert_chain(user_key)
      self._https_connection = httplib.HTTPSConnection(
        http_url.hostname,
        443 if port == 80 else port + 1,
        #timeout=,
        context=ssl_context,
      )

  def _request(self, connection, method, url, body=None, headers=None):
    path = self._path + url
    headers = headers or {}
    connection.request(method, path, body, headers)
    response = connection.getresponse()
    response_body = response.read()
    if response.status >= 400:
      raise CaucaseError(response.status, response.getheaders(), response_body)
    assert response.status < 300 # caucase does not redirect
    if response.status == 201:
      return response.getheader('Location')
    return response_body

  def _http(self, method, url, body=None, headers=None):
    return self._request(self._http_connection, method, url, body, headers)

  def _https(self, method, url, body=None, headers=None):
    return self._request(self._https_connection, method, url, body, headers)

  def getCertificateRevocationList(self):
    """
    [ANONYMOUS] Retrieve latest CRL.
    """
    return self._http('GET', '/crl')

  def getCertificateSigningRequest(self, csr_id):
    """
    [ANONYMOUS] Retrieve an CSR by its identifier.
    """
    return self._http('GET', '/csr/%i' % (csr_id, ))

  def getPendingCertificateRequestList(self):
    """
    [AUTHENTICATED] Retrieve all pending CSRs.
    """
    return [
      {
        y.encode('ascii'): z.encode('ascii') if isinstance(z, unicode) else z
        for y, z in x.iteritems()
      }
      for x in json.loads(self._https('GET', '/csr'))
    ]

  def createCertificateSigningRequest(self, csr):
    """
    [ANONYMOUS] Store a CSR and return its identifier.
    """
    return int(self._http('PUT', '/csr', csr, {
      'Content-Type': 'application/pkcs10',
    }))

  def deletePendingCertificateRequest(self, csr_id):
    """
    [AUTHENTICATED] Reject a pending CSR.
    """
    self._https('DELETE', '/csr/%i' % (csr_id, ))

  def _getCertificate(self, crt_id):
    return self._http('GET', '/crt' + crt_id)

  def getCertificate(self, csr_id):
    """
    [ANONYMOUS] Retrieve CRT by its identifier (same as corresponding CRL
    identifier).
    """
    return self._getCertificate('/%i' % (csr_id, ))

  def getCACertificate(self):
    """
    [ANONYMOUS] Retrieve current CA certificate.
    """
    return self._getCertificate('/ca.crt.pem')

  def getCACertificateChain(self):
    """
    [ANONYMOUS] Retrieve CA certificate chain, with CA certificate N+1 signed
    by CA certificate N, allowing automated CA cert rollout.
    """
    found = False
    previous_ca = trust_anchor = sorted(
      (
        utils.load_ca_certificate(x)
        for x in self._ca_crt_pem_list
      ),
      key=lambda x: x.not_valid_before,
    )[-1]
    result = []
    for entry in json.loads(self._getCertificate('/ca.crt.json')):
      try:
        payload = utils.unwrap(
          entry,
          lambda x: x['old_pem'],
          utils.DEFAULT_DIGEST_LIST,
        )
      except cryptography.exceptions.InvalidSignature:
        continue
      if not found:
        found = utils.load_ca_certificate(
          payload['old_pem'].encode('ascii'),
        ) == trust_anchor
      if found:
        if utils.load_ca_certificate(
          payload['old_pem'].encode('ascii'),
        ) != previous_ca:
          raise ValueError('CA signature chain broken')
        new_pem = payload['new_pem'].encode('ascii')
        result.append(new_pem)
        previous_ca = utils.load_ca_certificate(new_pem)
    return result

  def renewCertificate(self, old_crt, old_key, key_len):
    """
    [ANONYMOUS] Request certificate renewal.
    """
    new_key = utils.generatePrivateKey(key_len=key_len)
    return (
      utils.dump_privatekey(new_key),
      self._http(
        'PUT',
        '/crt/renew',
        json.dumps(
          utils.wrap(
            {
              'crt_pem': utils.dump_certificate(old_crt),
              'renew_csr_pem': utils.dump_certificate_request(
                x509.CertificateSigningRequestBuilder(
                ).subject_name(
                  # Note: caucase server ignores this, but cryptography
                  # requires CSRs to have a subject.
                  old_crt.subject,
                ).sign(
                  private_key=new_key,
                  algorithm=utils.DEFAULT_DIGEST_CLASS(),
                  backend=_cryptography_backend,
                ),
              ),
            },
            old_key,
            utils.DEFAULT_DIGEST,
          ),
        ),
        {'Content-Type': 'application/json'},
      ),
    )

  def revokeCertificate(self, crt, key=None):
    """
    Revoke certificate.
    [ANONYMOUS] if key is provided.
    [AUTHENTICATED] if key is missing.
    """
    if key:
      method = self._http
      data = utils.wrap(
        {
          'revoke_crt_pem': crt,
        },
        utils.load_privatekey(key),
        utils.DEFAULT_DIGEST,
      )
    else:
      method = self._https
      data = utils.nullWrap({
        'revoke_crt_pem': crt,
      })
    method(
      'PUT',
      '/crt/revoke',
      json.dumps(data),
      {'Content-Type': 'application/json'},
    )

  def revokeSerial(self, serial):
    """
    Revoke certificate by serial.

    This method is dangerous ! Prefer revokeCRT whenever possible.

    [AUTHENTICATED]
    """
    self._https(
      'PUT',
      '/crt/revoke',
      json.dumps(utils.nullWrap({'revoke_serial': serial})),
      {'Content-Type': 'application/json'},
    )

  def createCertificate(self, csr_id, template_csr=''):
    """
    [AUTHENTICATED] Sign certificate signing request.
    """
    header_dict = {}
    if template_csr:
      header_dict['Content-Type'] = 'application/pkcs10'
    self._https('PUT', '/crt/%i' % (csr_id, ), template_csr, header_dict)

class HTTPSOnlyCaucaseClient(CaucaseClient):
  """
  Like CaucaseClient, but forces anonymous accesses to go through HTTPS as
  well.
  """
  def __init__(self, *args, **kw):
    super(HTTPSOnlyCaucaseClient, self).__init__(*args, **kw)
    self._http_connection = self._https_connection
