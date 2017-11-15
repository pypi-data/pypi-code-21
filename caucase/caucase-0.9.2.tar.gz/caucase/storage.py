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
from random import getrandbits
import os
import sqlite3
from threading import local
from time import time
from .exceptions import NoStorage, NotFound, Found

__all__ = ('SQLite3Storage', )

DAY_IN_SECONDS = 60 * 60 * 24

class SQLite3Storage(local):
  """
  CA data storage.

  Every cryptographic type this class deals with must be PEM-encoded.
  """
  def __init__(
    self,
    db_path,
    table_prefix,
    max_csr_amount=50,
    crt_keep_time=1,
    crt_read_keep_time=0.05, # About 1 hour
    enforce_unique_key_id=False,
  ):
    """
    db_path (str)
      SQLite connection string.
    table_prefix (str)
      Name to use as a prefix for all tables managed by this storage adapter.
      Allows sharing the database, although it should only be within the same
      caucase process for access permission reasons.
    max_csr_amount (int)
      Maximum number of allowed pending certificate signing requests.
      To prevent flood.
    crt_keep_time (float)
      Time to keep signed certificates for, in days.
    crt_read_keep_time (float)
      Time to keep CRT content for after it was first read, in days.
      Allows requester to fail retrieving the certificate by tolerating
      retries.
    enforce_unique_key_id (bool)
      When true, certificate requests cannot be appended if there is already
      and known entry for the same private key.
      Note: this only makes sense if crt_keep_time and crt_read_keep_time are
      set at least to the certificate life span.
      Useful for backups, to ensure the certificate to revoke can be uniquely
      identified from the key used to decrypt the backup archive.
    """
    super(SQLite3Storage, self).__init__()
    self._db = db = sqlite3.connect(db_path)
    self._table_prefix = table_prefix
    db.row_factory = sqlite3.Row
    self._max_csr_amount = max_csr_amount
    self._crt_keep_time = crt_keep_time * DAY_IN_SECONDS
    self._crt_read_keep_time = crt_read_keep_time * DAY_IN_SECONDS
    with db:
      # Note about revoked.serial: certificate serials exceed the 63 bits
      # sqlite can accept as integers, so store these as text. Use a trivial
      # string serialisation: not very space efficient, but this should not be
      # a limiting issue for our use-cases anyway.
      db.cursor().executescript('''
        CREATE TABLE IF NOT EXISTS %(prefix)sca (
          expiration_date INTEGER,
          key TEXT,
          crt TEXT
        );
        CREATE TABLE IF NOT EXISTS %(prefix)scrt (
          id INTEGER PRIMARY KEY,
          key_id TEXT %(key_id_constraint)s,
          expiration_date INTEGER,
          csr TEXT,
          crt TEXT
        );
        CREATE TABLE IF NOT EXISTS %(prefix)srevoked (
          serial TEXT PRIMARY KEY,
          revocation_date INTEGER,
          expiration_date INTEGER
        );
        CREATE TABLE IF NOT EXISTS %(prefix)scrl (
          expiration_date INTEGER,
          crl TEXT
        );
        CREATE TABLE IF NOT EXISTS %(prefix)scounter (
          name TEXT PRIMARY KEY,
          value INTEGER
        );
        CREATE TABLE IF NOT EXISTS %(prefix)sconfig_once (
          name TEXT PRIMARY KEY,
          value TEXT
        )
      ''' % {
        'prefix': table_prefix,
        'key_id_constraint': 'UNIQUE' if enforce_unique_key_id else '',
      })

  def _incrementCounter(self, name, increment=1, initial=0):
    """
    Increment counter with <name> by <increment> and return resulting value.
    If <name> is not found, it is created with <initial>, and then incremented.
    Does not commit.
    """
    row = self._executeSingleRow(
      'SELECT value FROM %scounter WHERE name = ? LIMIT 2' % (
        self._table_prefix,
      ),
      (name, ),
    )
    if row is None:
      value = initial
    else:
      value = row['value']
    value += increment
    self._db.cursor().execute(
      'INSERT OR REPLACE INTO %scounter (name, value) VALUES (?, ?)' % (
        self._table_prefix,
      ),
      (name, value),
    )
    return value

  def _executeSingleRow(self, sql, parameters=()):
    """
    Execute <sql>, raise if it produces more than 1 row, and return it.
    """
    result_list = self._db.cursor().execute(sql, parameters).fetchall()
    if result_list:
      result, = result_list
      return result

  def getConfigOnce(self, name, default):
    """
    Retrieve the value of <name> from config-once list, or <default> if not
    stored.
    """
    with self._db:
      result = self._executeSingleRow(
        'SELECT value FROM %sconfig_once WHERE name = ?' % (
          self._table_prefix,
        ),
        (name, ),
      )
    if result is None:
      return default
    return result['value']

  def setConfigOnce(self, name, value):
    """
    Store <value> as <name> in config-once list, if it was not already stored.
    If it was already stored, do nothing.
    """
    try:
      with self._db as db:
        db.cursor().execute(
          'INSERT INTO %sconfig_once (name, value) VALUES (?, ?)' % (
            self._table_prefix,
          ),
          (name, value),
        )
    except sqlite3.IntegrityError:
      pass

  def getCAKeyPairList(self):
    """
    Return the chronologically sorted (oldest in [0], newest in [-1])
    certificate authority key pairs.
    """
    with self._db as db:
      c = db.cursor()
      c.execute(
        'DELETE FROM %sca WHERE expiration_date < ?' % (
          self._table_prefix,
        ),
        (time(), ),
      )
      return [
        {
          'crt_pem': x['crt'].encode('ascii'),
          'key_pem': x['key'].encode('ascii'),
        }
        for x in db.cursor().execute(
          'SELECT key, crt FROM %sca ORDER BY expiration_date ASC' % (
            self._table_prefix,
          ),
        ).fetchall()
      ]

  def appendCAKeyPair(self, expiration_timestamp, key_pair):
    """
    Store a certificate authority key pair.
    expiration_timestamp (int)
      Unix GMT timestamp of CA certificate "valid until" date.
    key_pair (dict with 'key' and 'crt' items)
      CA key pair to store, as bytes.
    """
    with self._db as db:
      db.cursor().execute(
        'INSERT INTO %sca (expiration_date, key, crt) VALUES (?, ?, ?)' % (
          self._table_prefix,
        ),
        (
          expiration_timestamp,
          key_pair['key_pem'],
          key_pair['crt_pem'],
        ),
      )

  def appendCertificateSigningRequest(
    self,
    csr_pem,
    key_id,
    override_limits=False,
  ):
    """
    Store acertificate signing request and generate a unique ID for it.
    Note: ID uniqueness is only guaranteed among pending CSR, and may be reused
    after the original CSR has been discarded (by being rejected or signed).
    """
    with self._db as db:
      known_csr = self._executeSingleRow(
        'SELECT id FROM %scrt WHERE csr = ? LIMIT 2' % (
          self._table_prefix,
        ),
        (csr_pem, ),
      )
      if known_csr is not None:
        return known_csr['id'], None
      if override_limits:
        # Ignore max pending count
        # Do not increment the number of auto-signed certificates, but do not
        # automatically sign either.
        requested_count = None
      else:
        if self._executeSingleRow(
          'SELECT COUNT(*) FROM %scrt WHERE crt IS NULL' % (
            self._table_prefix,
          )
        )[0] >= self._max_csr_amount:
          raise NoStorage
        requested_count = self._incrementCounter('received_csr')
      csr_id = getrandbits(63)
      c = db.cursor()
      c.execute(
        'INSERT INTO %scrt (id, key_id, csr) VALUES (?, ?, ?)' % (
          self._table_prefix,
        ),
        (
          csr_id,
          key_id,
          csr_pem,
        ),
      )
      c.execute(
        'DELETE FROM %scrt WHERE expiration_date < ?' % (
          self._table_prefix,
        ),
        (time(), ),
      )
      return csr_id, requested_count

  def deletePendingCertificateSigningRequest(self, csr_id):
    """
    Forget about a pending CSR. Does nothing if the CSR was already signed
    (it will be automatically garbage-collected later).
    Raises NotFound if there is no matching CSR.
    """
    with self._db as db:
      c = db.cursor()
      c.execute(
        'DELETE FROM %scrt WHERE id = ? AND crt IS NULL' % (
          self._table_prefix,
        ),
        (csr_id, ),
      )
      if c.rowcount == 1:
        return
      raise NotFound

  def getCertificateSigningRequest(self, csr_id):
    """
    Retrieve a PEM-encoded certificate signing request.

    csr_id (int)
      Desired CSR id, as given when the CSR was stored.

    Raises NotFound if there is no matching CSR.
    """
    with self._db:
      result = self._executeSingleRow(
        'SELECT csr FROM %scrt WHERE id = ?' % (
          self._table_prefix,
        ),
        (csr_id, ),
      )
      if result is None:
        raise NotFound
      return result['csr'].encode('ascii')

  def getCertificateSigningRequestList(self):
    """
    Return the list of all pending CSRs.

    Ignores any CSR for which a certificate was issued.
    """
    with self._db as db:
      return [
        {
          'id': str(x['id']),
          'csr': x['csr'].encode('ascii'),
        }
        for x in db.cursor().execute(
          'SELECT id, csr FROM %scrt WHERE crt IS NULL' % (
            self._table_prefix,
          ),
        ).fetchall()
      ]

  def storeCertificate(self, csr_id, crt):
    """
    Store certificate for pre-existing CSR.

    Raises NotFound if there is no matching CSR, or if a certificate was
    already stored.
    """
    with self._db as db:
      c = db.cursor()
      c.execute(
        'UPDATE %scrt SET crt=?, expiration_date = ? '
        'WHERE id = ? AND crt IS NULL' % (
          self._table_prefix,
        ),
        (
          crt,
          int(time() + self._crt_keep_time),
          csr_id,
        ),
      )
      if c.rowcount == 0:
        raise NotFound

  def getCertificate(self, crt_id):
    """
    Retrieve a PEM-encoded certificate.

    crt_id (int)
      Desired certificate id, which is the same as corresponding CSR's id.

    Raises NotFound if there is no matching CRT or if no certificate was issued
    for it.
    """
    with self._db as db:
      row = self._executeSingleRow(
        'SELECT crt, expiration_date FROM %scrt '
        'WHERE id = ? AND crt IS NOT NULL' % (
          self._table_prefix,
        ),
        (crt_id, ),
      )
      if row is None:
        raise NotFound
      new_expiration_date = int(time() + self._crt_read_keep_time)
      if row['expiration_date'] > new_expiration_date:
        db.cursor().execute(
          'UPDATE %scrt SET expiration_date = ? WHERE id = ?' % (
            self._table_prefix,
          ),
          (
            new_expiration_date,
            crt_id,
          )
        )
      return row['crt'].encode('ascii')

  def getCertificateByKeyIdentifier(self, key_id):
    """
    Return the certificate corresponding to given key_id.

    Raises NotFound if there is no matching CRT or if no certificate was issued
    for it.
    """
    with self._db:
      row = self._executeSingleRow(
        'SELECT crt FROM %scrt WHERE key_id = ? AND crt IS NOT NULL' % (
          self._table_prefix,
        ),
        (key_id, ),
      )
      if row is None:
        raise NotFound
      return row['crt'].encode('ascii')

  def iterCertificates(self):
    """
    Iterator over stored certificates.
    """
    with self._db as db:
      c = db.cursor()
      c.execute('SELECT crt FROM %scrt WHERE crt IS NOT NULL' % (
        self._table_prefix,
      ))
      while True:
        row = c.fetchone()
        if row is None:
          break
        yield row['crt'].encode('ascii')

  def revoke(self, serial, expiration_date):
    """
    Add given certificate serial to the list of revoked certificates.
    Flushes any current CRL.

    serial (int)
      Serial of the certificate to revoke.
    expiration_date (int)
      Unix timestamp at which the certificate expires, allowing to remove this
      entry from the CRL.
    """
    with self._db as db:
      c = db.cursor()
      c.execute('DELETE FROM %scrl' % (
        self._table_prefix,
      ))
      try:
        c.execute(
          'INSERT INTO %srevoked '
          '(serial, revocation_date, expiration_date) '
          'VALUES (?, ?, ?)' % (
            self._table_prefix,
          ),
          (
            str(serial),
            int(time()),
            expiration_date,
          )
        )
      except sqlite3.IntegrityError:
        raise Found

  def getCertificateRevocationList(self):
    """
    Get PEM-encoded current Certificate Revocation List.

    Returns None if there is no CRL.
    """
    with self._db:
      row = self._executeSingleRow(
        'SELECT crl FROM %scrl '
        'WHERE expiration_date > ? ORDER BY expiration_date DESC LIMIT 1' % (
          self._table_prefix,
        ),
        (time(), )
      )
      if row is not None:
        return row['crl'].encode('ascii')

  def getNextCertificateRevocationListNumber(self):
    """
    Get next CRL sequence number.
    """
    return self._incrementCounter('crl_number')

  def storeCertificateRevocationList(self, crl, expiration_date):
    """
    Store Certificate Revocation List.
    """
    with self._db as db:
      c = db.cursor()
      c.execute('DELETE FROM %scrl' % (
        self._table_prefix,
      ))
      c.execute(
        'INSERT INTO %scrl (expiration_date, crl) VALUES (?, ?)' % (
          self._table_prefix,
        ),
        (
          int(expiration_date),
          crl,
        ),
      )

  def getRevocationList(self):
    """
    Get the list of all revoked certificates.

    Returns a list of dicts, each containing:
    - revocation_date (int)
      Unix timestamp of certificate revocation.
    - serial (int)
      Revoked certificate's serial.
    """
    with self._db as db:
      c = db.cursor()
      c.execute(
        'DELETE FROM %srevoked WHERE expiration_date < ?' % (
          self._table_prefix,
        ),
        (time(), ),
      )
      return [
        {
          'revocation_date': int(x['revocation_date']),
          'serial': int(x['serial']),
        }
        for x in c.execute(
          'SELECT revocation_date, serial FROM %srevoked' % (
            self._table_prefix,
          ),
        )
      ]

  def dumpIterator(self):
    """
    Backs the *entire* dabase up. This is not limited to tables managed by this
    class (so not limited to table_prefix).
    """
    for statement in self._db.iterdump():
      yield statement.encode('utf-8') + '\0'

  @staticmethod
  def restore(db_path, restorator):
    """
    Restores a dump which is the concatenated output of dumpIterator.
    Should not be called directly, but via
    ca.CertificateAuthority.restoreBackup .

    db_path (str)
      Path to the SQLite database to produce. Must not exist.

    read (callabla taking an integer as argument)
      Must return this many bytes, or an empty string if there is no input
      left.
    """
    buf = ''
    if os.path.exists(db_path):
      raise ValueError('%r exists, not restoring.' % (db_path, ))
    c = sqlite3.connect(db_path, isolation_level=None).cursor()
    for chunk in restorator:
      statement_list = (buf + chunk).split('\0')
      buf = statement_list.pop()
      for statement in statement_list:
        c.execute((statement).decode('utf-8'))
    if buf:
      raise ValueError('Short read, backup truncated ?')
