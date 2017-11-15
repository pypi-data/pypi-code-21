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
from __future__ import absolute_import, print_function
import argparse
from collections import defaultdict
import datetime
from getpass import getpass
import glob
import os
import socket
from SocketServer import ThreadingMixIn
import ssl
import sys
import tempfile
from threading import Thread
from urlparse import urlparse
from wsgiref.simple_server import make_server, WSGIServer
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import pem
from . import exceptions
from . import utils
from .wsgi import Application
from .ca import CertificateAuthority, UserCertificateAuthority
from .storage import SQLite3Storage
from .http_wsgirequesthandler import WSGIRequestHandler

_cryptography_backend = default_backend()

BACKUP_SUFFIX = '.sql.caucased'

def getBytePass(prompt): # pragma: no cover
  """
  Like getpass, but resurns a bytes instance.
  """
  result = getpass(prompt)
  if not isinstance(result, bytes):
    result = result.encode(sys.stdin.encoding)
  return result

def _createKey(path):
  """
  Open a key file, setting it to minimum permission if it gets created.
  Does not change umask, to be thread-safe.

  Returns a python file object, opened for write-only.
  """
  return os.fdopen(
    os.open(path, os.O_WRONLY | os.O_CREAT, 0o600),
    'w',
  )

class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
  """
  Threading WSGI server
  """
  daemon_threads = True

  def __init__(self, server_address, *args, **kw):
    self.address_family, _, _, _, _ = socket.getaddrinfo(*server_address)[0]
    assert self.address_family in (socket.AF_INET, socket.AF_INET6), (
      self.address_family,
    )
    WSGIServer.__init__(self, server_address, *args, **kw)

class CaucaseWSGIRequestHandler(WSGIRequestHandler):
  """
  Make WSGIRequestHandler logging more apache-like.
  """
  def log_date_time_string(self):
    """
    Apache-style date format.

    Compared to python's default (from BaseHTTPServer):
    - ":" between day and time
    - "+NNNN" timezone is displayed
    - ...but, because of how impractical it is in python to get system current
      timezone (including DST considerations), time it always logged in GMT
    """
    now = datetime.datetime.utcnow()
    return now.strftime(
      '%d/' + self.monthname[now.month] + '/%Y:%H:%M:%S +0000',
    )

class CaucaseSSLWSGIRequestHandler(CaucaseWSGIRequestHandler):
  """
  Add SSL-specific entries to environ:
  - HTTPS=on
  - SSL_CLIENT_CERT when client has sent a certificate.
  """
  ssl_client_cert_serial = '-'
  def get_environ(self):
    """
    Populate environment.
    """
    environ = CaucaseWSGIRequestHandler.get_environ(self)
    environ['HTTPS'] = 'on'
    client_cert_der = self.request.getpeercert(binary_form=True)
    if client_cert_der is not None:
      cert = x509.load_der_x509_certificate(
        client_cert_der,
        _cryptography_backend,
      )
      self.ssl_client_cert_serial = str(cert.serial_number)
      environ['SSL_CLIENT_CERT'] = utils.dump_certificate(cert)
    return environ

  # pylint: disable=redefined-builtin
  def log_message(self, format, *args):
    # Note: compared to BaseHTTPHandler, logs the client certificate serial as
    # user name.
    sys.stderr.write(
      "%s - %s [%s] %s\n" % (
        self.client_address[0],
        self.ssl_client_cert_serial,
        self.log_date_time_string(),
        format % args,
      )
    )
  # pylint: enable=redefined-builtin

def startServerThread(server):
  """
  Create and start a "serve_forever" thread, and return it.
  """
  server_thread = Thread(target=server.serve_forever)
  server_thread.daemon = True
  server_thread.start()

def updateSSLContext(
  https,
  key_len,
  threshold,
  server_key_path,
  hostname,
  cau,
  cas,
  wrap=False,
):
  """
  Build a new SSLContext with updated CA certificates, CRL and server key pair,
  apply it to <https>.socket and return the datetime of next update.
  """
  ssl_context = ssl.create_default_context(
    purpose=ssl.Purpose.CLIENT_AUTH,
  )
  # SSL is used for client authentication, and is only required for very few
  # users on any given caucased. So make ssl_context even stricter than python
  # does.
  # No TLSv1 and TLSv1.1, leaving (currently) only TLSv1.2
  ssl_context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1

  # If a client wishes to use https for unauthenticated operations, that's
  # fine too.
  ssl_context.verify_mode = ssl.CERT_OPTIONAL
  # Note: it does not seem possible to get python's openssl context to check
  # certificate revocation:
  # - calling load_verify_locations(cadata=<crl data>) or
  #   load_verify_locations(cadata=<crl data> + <ca crt data>) raises
  # - calling load_verify_locations(cadata=<ca crt data> + <crl data>) fails to
  #   validate CA completely
  # Anyway, wsgi application level is supposed (and automatically tested to)
  # verify revocations too, so this should not be a big issue... Still,
  # implementation cross-check would have been nice.
  #ssl_context.verify_flags = ssl.VERIFY_CRL_CHECK_LEAF
  ssl_context.load_verify_locations(
    cadata=cau.getCACertificate().decode('ascii'),
  )
  cas_certificate_list = cas.getCACertificateList()
  threshold_delta = datetime.timedelta(threshold, 0)
  if os.path.exists(server_key_path):
    old_crt_pem = utils.getCert(server_key_path)
    old_crt = utils.load_certificate(old_crt_pem, cas_certificate_list, None)
    if old_crt.not_valid_after - threshold_delta < datetime.datetime.utcnow():
      new_key = utils.generatePrivateKey(key_len)
      new_key_pem = utils.dump_privatekey(new_key)
      new_crt_pem = cas.renew(
        crt_pem=old_crt_pem,
        csr_pem=utils.dump_certificate_request(
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
      )
      with _createKey(server_key_path) as crt_file:
        crt_file.write(new_key_pem)
        crt_file.write(new_crt_pem)
  else:
    new_key = utils.generatePrivateKey(key_len)
    csr_id = cas.appendCertificateSigningRequest(
      csr_pem=utils.dump_certificate_request(
        x509.CertificateSigningRequestBuilder(
        ).subject_name(
          x509.Name([
            x509.NameAttribute(
              oid=x509.oid.NameOID.COMMON_NAME,
              value=hostname.decode('ascii'),
            ),
          ]),
        ).add_extension(
          x509.KeyUsage(
            # pylint: disable=bad-whitespace
            digital_signature =True,
            content_commitment=False,
            key_encipherment  =True,
            data_encipherment =False,
            key_agreement     =False,
            key_cert_sign     =False,
            crl_sign          =False,
            encipher_only     =False,
            decipher_only     =False,
            # pylint: enable=bad-whitespace
          ),
          critical=True,
        ).add_extension(
          x509.SubjectAlternativeName([
            x509.DNSName(hostname.decode('ascii')),
          ]),
          critical=True,
        ).sign(
          private_key=new_key,
          algorithm=utils.DEFAULT_DIGEST_CLASS(),
          backend=_cryptography_backend,
        ),
      ),
      override_limits=True,
    )
    cas.createCertificate(csr_id)
    new_crt_pem = cas.getCertificate(csr_id)
    new_key_pem = utils.dump_privatekey(new_key)
    with _createKey(server_key_path) as crt_file:
      crt_file.write(new_key_pem)
      crt_file.write(new_crt_pem)
  ssl_context.load_cert_chain(server_key_path)
  if wrap:
    https.socket = ssl_context.wrap_socket(
      sock=https.socket,
      server_side=True,
    )
  else:
    https.socket.context = ssl_context
  return utils.load_certificate(
    utils.getCert(server_key_path),
    cas_certificate_list,
    None,
  ).not_valid_after - threshold_delta

def main(argv=None, until=utils.until):
  """
  Caucase stand-alone http server.
  """
  parser = argparse.ArgumentParser(description='caucased')
  parser.add_argument(
    '--db',
    default='caucase.sqlite',
    help='Path to the SQLite database. default: %(default)s',
  )
  parser.add_argument(
    '--server-key',
    default='server.key.pem',
    metavar='KEY_PATH',
    help='Path to the ssl key pair to use for https socket. '
    'default: %(default)s',
  )
  parser.add_argument(
    '--netloc',
    required=True,
    help='<host>[:<port>] of HTTP socket. '
    'HTTPS socket netloc will be deduced following caucase rules: if port is '
    '80 or not provided, https port will be 443, else it will be port + 1. '
    'If not provided, http port will be picked among available ports and '
    'https port will be the next port. Also, signed certificates will not '
    'contain a CRL distribution point URL. If https port is not available, '
    'this program will exit with an aerror status. '
    'Note on encoding: only ascii is currently supported. Non-ascii may be '
    'provided idna-encoded.',
  )
  parser.add_argument(
    '--threshold',
    default=31,
    type=float,
    help='The remaining certificate validity period, in days, under '
    'which a renew is desired. default: %(default)s',
  )
  parser.add_argument(
    '--key-len',
    default=2048,
    type=int,
    metavar='BITLENGTH',
    help='Number of bits to use when generating a new private key. '
    'default: %(default)s',
  )

  service_group = parser.add_argument_group(
    'CAS options: normal certificates, which are not given any privilege on '
    'caucased',
  )

  user_group = parser.add_argument_group(
    'CAU options: special certificates, which are allowed to sign other '
    'certificates and can decrypt backups',
  )

  service_group.add_argument(
    '--service-crt-validity',
    default=3 * 31,
    type=float,
    metavar='DAYS',
    help='Number of days an issued certificate is valid for. '
    'default: %(default)s',
  )
  user_group.add_argument(
    '--user-crt-validity',
    default=3 * 31,
    type=float,
    metavar='DAYS',
    help='Number of days an issued certificate is valid for. '
    'default: %(default)s',
  )

  service_group.add_argument(
    '--service-max-csr',
    default=50,
    type=int,
    help='Maximum number of pending CSR. Further CSR get refused until '
    'an existing ones gets signed or rejected. default: %(default)s',
  )
  user_group.add_argument(
    '--user-max-csr',
    default=50,
    type=int,
    help='Maximum number of pending CSR. Further CSR get refused until '
    'an existing ones gets signed or rejected. default: %(default)s',
  )

  service_group.add_argument(
    '--service-auto-approve-count',
    default=0,
    type=int,
    metavar='COUNT',
    help='Number service certificates which should be automatically signed on '
    'submission, excluding the one needed to serve caucase. '
    'default: %(default)s'
  )
  user_group.add_argument(
    '--user-auto-approve-count',
    default=1,
    type=int,
    metavar='COUNT',
    help='Number of user certificates which should be automatically signed on '
    'submission. default: %(default)s',
  )
  parser.add_argument(
    '--lock-auto-approve-count',
    action='store_true',
    help='The first time this option is given, --service-auto-approve-count '
    'and --user-auto-approve-count values are stored inside caucase database '
    'and will not be altered by further invocations. Once the respective '
    'certificate issuance counters reach these values, no further '
    'certificates will be ever automatically signed.'
  )

  backup_group = parser.add_argument_group(
    'Backup options',
  )
  backup_group.add_argument(
    '--backup-directory',
    help='Backup directory path. Backups will be periodically stored in '
    'given directory, encrypted with all certificates which are valid at the '
    'time of backup generation. Any one of the associated private keys can '
    'decypher it. If not set, no backup will be created.',
  )
  backup_group.add_argument(
    '--backup-period',
    default=1,
    type=float,
    help='Number of days between backups. default: %(default)s'
  )
  args = parser.parse_args(argv)

  base_url = u'http://' + args.netloc.decode('ascii')
  parsed_base_url = urlparse(base_url)
  hostname = parsed_base_url.hostname
  http_port = parsed_base_url.port
  cau_crt_life_time = args.user_crt_validity
  cau = UserCertificateAuthority(
    storage=SQLite3Storage(
      db_path=args.db,
      table_prefix='cau',
      max_csr_amount=args.user_max_csr,
      # Effectively disables certificate expiration
      crt_keep_time=cau_crt_life_time,
      crt_read_keep_time=cau_crt_life_time,
      enforce_unique_key_id=True,
    ),
    ca_subject_dict={
      'CN': u'Caucase CAU' + (
        u'' if base_url is None else u' at ' + base_url + '/cau'
      ),
    },
    ca_key_size=args.key_len,
    crt_life_time=cau_crt_life_time,
    auto_sign_csr_amount=args.user_auto_approve_count,
    lock_auto_sign_csr_amount=args.lock_auto_approve_count,
  )
  cas = CertificateAuthority(
    storage=SQLite3Storage(
      db_path=args.db,
      table_prefix='cas',
      max_csr_amount=args.service_max_csr,
    ),
    ca_subject_dict={
      'CN': u'Caucase CAS' + (
        u'' if base_url is None else u' at ' + base_url + '/cas'
      ),
    },
    crl_base_url=None if base_url is None else base_url + u'/cas/crl',
    ca_key_size=args.key_len,
    crt_life_time=args.service_crt_validity,
    auto_sign_csr_amount=args.service_auto_approve_count,
    lock_auto_sign_csr_amount=args.lock_auto_approve_count,
  )
  application = Application(cau=cau, cas=cas)
  http = make_server(
    host=hostname,
    port=http_port,
    app=application,
    server_class=ThreadingWSGIServer,
    handler_class=CaucaseWSGIRequestHandler,
  )
  https = make_server(
    host=hostname,
    port=443 if http_port == 80 else http_port + 1,
    app=application,
    server_class=ThreadingWSGIServer,
    handler_class=CaucaseSSLWSGIRequestHandler,
  )
  next_deadline = next_ssl_update = updateSSLContext(
    https=https,
    key_len=args.key_len,
    threshold=args.threshold,
    server_key_path=args.server_key,
    hostname=hostname,
    cau=cau,
    cas=cas,
    wrap=True,
  )
  if args.backup_directory:
    backup_period = datetime.timedelta(args.backup_period, 0)
    try:
      next_backup = max(
        datetime.datetime.utcfromtimestamp(os.stat(x).st_ctime)
        for x in glob.iglob(
          os.path.join(args.backup_directory, '*' + BACKUP_SUFFIX),
        )
      ) + backup_period
    except ValueError:
      next_backup = datetime.datetime.utcnow()
    next_deadline = min(
      next_deadline,
      next_backup,
    )
  else:
    next_backup = None
  startServerThread(http)
  startServerThread(https)
  try:
    while True:
      now = until(next_deadline)
      if now >= next_ssl_update:
        next_ssl_update = updateSSLContext(
          https=https,
          key_len=args.key_len,
          threshold=args.threshold,
          server_key_path=args.server_key,
          hostname=hostname,
          cau=cau,
          cas=cas,
        )
      if next_backup is None:
        next_deadline = next_ssl_update
      else:
        if now >= next_backup:
          tmp_backup_fd, tmp_backup_path = tempfile.mkstemp(
            prefix='caucase_backup_',
          )
          with os.fdopen(tmp_backup_fd, 'w') as backup_file:
            result = cau.doBackup(backup_file.write)
          if result:
            backup_path = os.path.join(
              args.backup_directory,
              now.strftime('%Y%m%d%H%M%S') + BACKUP_SUFFIX,
            )
            os.rename(tmp_backup_path, backup_path)
            next_backup = now + backup_period
          else:
            os.unlink(tmp_backup_path)
            next_backup = now + datetime.timedelta(0, 3600)
        next_deadline = min(
          next_ssl_update,
          next_backup,
        )
  except utils.SleepInterrupt:
    pass
  finally:
    https.shutdown()
    http.shutdown()

def manage(argv=None):
  """
  caucased database management tool.
  """
  parser = argparse.ArgumentParser(
    description='caucased caucased database management tool',
  )
  parser.add_argument(
    '--db',
    default='caucase.sqlite',
    help='Path to the SQLite database. default: %(default)s',
  )
  parser.add_argument(
    '--user-crt-validity',
    default=3 * 31,
    type=float,
    metavar='DAYS',
    help='Number of days an issued certificate is valid for. Useful with '
    '--restore-backup as a new user certificate must be produced. '
    'default: %(default)s',
  )

  parser.add_argument(
    '--restore-backup',
    nargs=4,
    metavar=('BACKUP_PATH', 'KEY_PATH', 'CSR_PATH', 'CRT_PATH'),
    help='Restore the file at BACKUP_PATH, decyphering it with the key '
    'at KEY_PATH, revoking corresponding certificate and issuing a new '
    'one in CRT_PATH using the public key in CSR_PATH. '
    'Fails if database exists.',
  )
  parser.add_argument(
    '--import-ca',
    default=[],
    metavar='PEM_FILE',
    action='append',
    type=argparse.FileType('r'),
    help='Import key pairs as initial service CA certificate. '
    'May be provided multiple times to import multiple key pairs. '
    'Keys and certificates may be in separate files. '
    'If there are multiple keys or certificates, all will be imported. '
    'Will fail if there is any certificate without a key, or vice-versa, '
    'or if any certificate is not suitable for use as a CA certificate. '
    'Caucase-initiated CA renewal, which will happen when latest provided '
    'has less than 3 times --service-crt-validity validity period left, '
    'will copy that CA\'s extensions to produce the new certificate. '
    'Passphrase will be prompted for each protected key.',
  )
  parser.add_argument(
    '--import-bad-ca',
    action='store_true',
    default=False,
    help='Do not check sanity of imported CA certificates. Useful when '
    'migrating a custom CA where clients do very customised checks. Do not '
    'use this unless you are certain you need it and it is safe for your '
    'use-case.',
  )
  parser.add_argument(
    '--import-crl',
    default=[],
    metavar='PEM_FILE',
    action='append',
    type=argparse.FileType('r'),
    help='Import service revocation list. Corresponding CA certificate must '
    'be already present in the database (including added in the same run '
    'using --import-ca).',
  )
  parser.add_argument(
    '--export-ca',
    metavar='PEM_FILE',
    type=argparse.FileType('w'),
    help='Export all CA certificates in a PEM file. Passphrase will be '
    'prompted to protect all keys.',
  )
  args = parser.parse_args(argv)
  db_path = args.db
  if args.restore_backup:
    (
      backup_path,
      backup_key_path,
      backup_csr_path,
      backup_crt_path,
    ) = args.restore_backup
    try:
      _, key_pem, _ = utils.getKeyPair(backup_key_path)
    except ValueError:
      # maybe user extracted their private key ?
      key_pem = utils.getKey(backup_key_path)
    cau_crt_life_time = args.user_crt_validity
    with open(backup_path) as backup_file:
      with open(backup_crt_path, 'a') as new_crt_file:
        new_crt_file.write(
          UserCertificateAuthority.restoreBackup(
            db_class=SQLite3Storage,
            db_path=db_path,
            read=backup_file.read,
            key_pem=key_pem,
            csr_pem=utils.getCertRequest(backup_csr_path),
            db_kw={
              'table_prefix': 'cau',
              # max_csr_amount: not needed, renewal ignores quota
              # Effectively disables certificate expiration
              'crt_keep_time': cau_crt_life_time,
              'crt_read_keep_time': cau_crt_life_time,
              'enforce_unique_key_id': True,
            },
            kw={
              # Disable CA cert renewal
              'ca_key_size': None,
              'crt_life_time': cau_crt_life_time,
            },
          ),
        )
  if args.import_ca:
    import_ca_dict = defaultdict(
      (lambda: {'crt': None, 'key': None, 'from': []}),
    )
    for ca_file in args.import_ca:
      for index, component in enumerate(pem.parse(ca_file.read())):
        name = '%r, block %i' % (ca_file.name, index)
        if isinstance(component, pem.Certificate):
          component_name = 'crt'
          component_value = x509.load_pem_x509_certificate(
            component.as_bytes(),
            _cryptography_backend,
          )
        elif isinstance(component, pem.Key):
          password = None
          while True:
            component_name = 'key'
            try:
              component_value = serialization.load_pem_private_key(
                component.as_bytes(),
                password,
                _cryptography_backend,
              )
            except TypeError:
              password = getBytePass('Passphrase for key at %s: ' % (name, ))
            else:
              break
        else:
          raise TypeError('%s is of unsupported type %r' % (
            name,
            type(component),
          ))
        import_ca = import_ca_dict[
          x509.SubjectKeyIdentifier.from_public_key(
            component_value.public_key(),
          ).digest
        ]
        import_ca[component_name] = component_value
        import_ca['from'].append(name)
    now = utils.datetime2timestamp(datetime.datetime.utcnow())
    imported = 0
    cas_db = SQLite3Storage(
      db_path,
      table_prefix='cas',
    )
    for identifier, ca_pair in import_ca_dict.iteritems():
      found_from = ', '.join(ca_pair['from'])
      crt = ca_pair['crt']
      if crt is None:
        print('No certificate correspond to ' + found_from + ', skipping')
        continue
      expiration = utils.datetime2timestamp(crt.not_valid_after)
      if expiration < now:
        print('Skipping expired certificate from ' + found_from)
        del import_ca_dict[identifier]
        continue
      if not args.import_bad_ca:
        try:
          basic_contraints = crt.extensions.get_extension_for_class(
            x509.BasicConstraints,
          )
          key_usage = crt.extensions.get_extension_for_class(
            x509.KeyUsage,
          ).value
        except x509.ExtensionNotFound:
          failed = True
        else:
          failed = (
            not basic_contraints.value.ca or not basic_contraints.critical
            or not key_usage.key_cert_sign or not key_usage.crl_sign
          )
        if failed:
          print('Skipping non-CA certificate from ' + found_from)
          continue
      key = ca_pair['key']
      if key is None:
        print('No private key correspond to ' + found_from + ', skipping')
        continue
      imported += 1
      cas_db.appendCAKeyPair(
        expiration,
        {
          'key_pem': utils.dump_privatekey(key),
          'crt_pem': utils.dump_certificate(crt),
        },
      )
    if not imported:
      raise ValueError('No CA certificate imported')
    print('Imported %i CA certificates' % imported)
  if args.import_crl:
    db = SQLite3Storage(db_path, table_prefix='cas')
    trusted_ca_crt_set = [
      utils.load_ca_certificate(x['crt_pem'])
      for x in db.getCAKeyPairList()
    ]
    latest_ca_not_after = max(
      x.not_valid_after
      for x in trusted_ca_crt_set
    )
    already_revoked_count = revoked_count = 0
    for crl_file in args.import_crl:
      for revoked in utils.load_crl(crl_file.read(), trusted_ca_crt_set):
        try:
          db.revoke(
            revoked.serial_number,
            latest_ca_not_after,
          )
        except exceptions.Found:
          already_revoked_count += 1
        else:
          revoked_count += 1
    print('Revoked %i certificates (%i were already revoked)' % (
      revoked_count,
      already_revoked_count,
    ))
  if args.export_ca is not None:
    encryption_algorithm = serialization.BestAvailableEncryption(
      getBytePass('CA export passphrase: ')
    )
    write = args.export_ca.write
    for key_pair in SQLite3Storage(
      db_path,
      table_prefix='cas',
    ).getCAKeyPairList():
      write(
        key_pair['crt_pem'] + serialization.load_pem_private_key(
          key_pair['key_pem'],
          None,
          _cryptography_backend,
        ).private_bytes(
          encoding=serialization.Encoding.PEM,
          format=serialization.PrivateFormat.TraditionalOpenSSL,
          encryption_algorithm=encryption_algorithm,
        ),
      )
    args.export_ca.close()
