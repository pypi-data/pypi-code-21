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

class CertificateAuthorityException(Exception):
  """Base exception"""
  pass

class NoStorage(CertificateAuthorityException):
  """No space in storage"""
  pass

class NotFound(CertificateAuthorityException):
  """Requested resource does not exist"""
  pass

class Found(CertificateAuthorityException):
  """Resource to create already exists"""
  pass

class CertificateVerificationError(CertificateAuthorityException):
  """Certificate is not valid, it was not signed by CA"""
  pass

class NotACertificateSigningRequest(CertificateAuthorityException):
  """Provided value is not a certificate signing request"""
  pass

class NotJSON(CertificateAuthorityException):
  """Provided value does not decode properly as JSON"""
  pass
