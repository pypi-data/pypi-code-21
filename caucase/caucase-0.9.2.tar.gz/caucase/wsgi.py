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
import httplib
import json
import traceback
from . import utils
from . import exceptions

__all__ = ('Application', )

SUBPATH_FORBIDDEN = object()
SUBPATH_REQUIRED = object()
SUBPATH_OPTIONAL = object()

def _getStatus(code):
  return '%i %s' % (code, httplib.responses[code])

class ApplicationError(Exception):
  """
  WSGI HTTP error base class.
  """
  status = _getStatus(httplib.INTERNAL_SERVER_ERROR)
  _response_headers = []

  @property
  def response_headers(self):
    """
    Get a copy of error's response headers.
    """
    return self._response_headers[:]

class BadRequest(ApplicationError):
  """
  HTTP bad request error
  """
  status = _getStatus(httplib.BAD_REQUEST)

class Unauthorized(ApplicationError):
  """
  HTTP unauthorized error
  """
  status = _getStatus(httplib.UNAUTHORIZED)

class SSLUnauthorized(Unauthorized):
  """
  Authentication failed because of SSL credentials (missing or incorrect)
  """
  _response_headers = [
    # Note: non standard scheme, suggested in
    # https://www.ietf.org/mail-archive/web/httpbisa/current/msg03764.html
    ('WWW-Authenticate', 'transport'),
  ]

class NotFound(ApplicationError):
  """
  HTTP not found error
  """
  status = _getStatus(httplib.NOT_FOUND)

class BadMethod(ApplicationError):
  """
  HTTP bad method error
  """
  status = _getStatus(httplib.METHOD_NOT_ALLOWED)

class Conflict(ApplicationError):
  """
  HTTP conflict
  """
  status = _getStatus(httplib.CONFLICT)

class TooLarge(ApplicationError):
  """
  HTTP too large error
  """
  status = _getStatus(httplib.REQUEST_ENTITY_TOO_LARGE)

class InsufficientStorage(ApplicationError):
  """
  No storage slot available (not necessarily out of disk space)
  """
  # httplib lacks the textual description for 507, although it has the
  # constant...
  status = '%i Insufficient Storage' % (httplib.INSUFFICIENT_STORAGE, )

STATUS_OK = _getStatus(httplib.OK)
STATUS_CREATED = _getStatus(httplib.CREATED)
STATUS_NO_CONTENT = _getStatus(httplib.NO_CONTENT)
MAX_BODY_LENGTH = 10 * 1024 * 1024 # 10 MB

class Application(object):
  """
  WSGI application class

  Thread- and process-safe (locks handled by sqlite3).
  """
  def __init__(self, cau, cas):
    """
    cau (caucase.ca.CertificateAuthority)
      CA for users.
      Will be hosted under /cau

    cas (caucase.ca.CertificateAuthority)
      CA for services.
      Will be hosted under /cas
    """
    self._cau = cau
    # Routing dict structure:

    # path entry dict:
    # "method": method dict
    # "context": any object
    # "routing": routing dict

    # routing dict:
    # key: path entry (ie, everything but slashes)
    # value: path entry dict

    # method dict:
    # key: HTTP method ("GET", "POST", ...)
    # value: action dict

    # action dict:
    # "do": callable for the action
    #   If "subpath" forbidden:
    #     (context, environ) -> (status, header_list, iterator)
    #   Otherwise:
    #     (context, environ, subpath) -> (status, header_list, iterator)
    # - context is the value of the nearest path entry dict's "context", None
    #   by default.
    # - environ: wsgi environment
    # - subpath: trailing path component list
    # - status: HTTP status code & reason
    # - header_list: HTTP reponse header list (see wsgi specs)
    # - iterator: HTTP response body generator (see wsgi specs)
    # "subpath": whether a subpath is expected, forbidden, or optional
    #   (default: forbidden)

    caucase_routing_dict = {
      'crl': {
        'method': {
          'GET': {
            'do': self.getCertificateRevocationList,
          },
        },
      },
      'csr': {
        'method': {
          'GET': {
            'do': self.getCSR,
            'subpath': SUBPATH_OPTIONAL,
          },
          'PUT': {
            'do': self.createCertificateSigningRequest,
          },
          'DELETE': {
            'do': self.deletePendingCertificateRequest,
            'subpath': SUBPATH_REQUIRED,
          },
        },
      },
      'crt': {
        'routing': {
          'ca.crt.pem': {
            'method': {
              'GET': {
                'do': self.getCACertificate,
              },
            },
          },
          'ca.crt.json': {
            'method': {
              'GET': {
                'do': self.getCACertificateChain,
              },
            },
          },
          'revoke': {
            'method': {
              'PUT': {
                'do': self.revokeCertificate,
              },
            },
          },
          'renew': {
            'method': {
              'PUT': {
                'do': self.renewCertificate,
              },
            },
          },
        },
        'method': {
          'GET': {
            'do': self.getCertificate,
            'subpath': SUBPATH_REQUIRED,
          },
          'PUT': {
            'do': self.createCertificate,
            'subpath': SUBPATH_REQUIRED,
          },
        },
      },
    }
    self._root_dict = {
      'routing': {
        'cas': {
          'context': cas,
          'routing': caucase_routing_dict,
        },
        'cau': {
          'context': cau,
          'routing': caucase_routing_dict,
        },
      },
    }

  def __call__(self, environ, start_response):
    """
    WSGI entry point
    """
    try: # Convert ApplicationError subclasses into error responses
      try: # Convert exceptions into ApplicationError subclass exceptions
        path_item_list = [
          x
          for x in environ.get('PATH_INFO', '').split('/')
          if x
        ]
        path_entry_dict = self._root_dict
        context = None
        while path_item_list:
          context = path_entry_dict.get('context', context)
          try:
            path_entry_dict = path_entry_dict['routing'][path_item_list[0]]
          except KeyError:
            break
          del path_item_list[0]
        try:
          method_dict = path_entry_dict['method']
        except KeyError:
          raise NotFound
        request_method = environ['REQUEST_METHOD']
        try:
          action_dict = method_dict[request_method]
        except KeyError:
          if request_method == 'OPTIONS':
            status = STATUS_NO_CONTENT
            header_list = []
            result = []
          else:
            raise BadMethod
        else:
          subpath = action_dict.get('subpath', SUBPATH_FORBIDDEN)
          if (
            subpath is SUBPATH_FORBIDDEN and path_item_list or
            subpath is SUBPATH_REQUIRED and not path_item_list
          ):
            raise NotFound
          if action_dict.get('context_is_routing'):
            context = path_entry_dict.get('routing')
          kw = {
            'context': context,
            'environ': environ,
          }
          if subpath != SUBPATH_FORBIDDEN:
            kw['subpath'] = path_item_list
          status, header_list, result = action_dict['do'](**kw)
      except ApplicationError:
        raise
      except exceptions.NotFound:
        raise NotFound
      except exceptions.Found:
        raise Conflict
      except exceptions.NoStorage:
        raise InsufficientStorage
      except exceptions.NotJSON:
        raise BadRequest('Invalid json payload')
      except exceptions.CertificateAuthorityException, e:
        raise BadRequest(str(e))
      except Exception:
        environ['wsgi.errors'].write('Unhandled exception\n')
        traceback.print_exc(file=environ['wsgi.errors'])
        raise ApplicationError
    except ApplicationError, e:
      status = e.status
      header_list = e.response_headers
      result = [str(x) for x in e.args]
    start_response(status, header_list)
    return result

  @staticmethod
  def _returnFile(data, content_type, header_list=None):
    if header_list is None:
      header_list = []
    header_list.append(('Content-Type', content_type))
    header_list.append(('Content-Length', str(len(data))))
    return (STATUS_OK, header_list, [data])

  @staticmethod
  def _getCSRID(subpath):
    try:
      crt_id, = subpath
    except ValueError:
      raise NotFound
    try:
      return int(crt_id)
    except ValueError:
      raise BadRequest('Invalid integer')

  @staticmethod
  def _read(environ):
    """
    Read the entire request body.

    Raises BadRequest if request Content-Length cannot be parsed.
    Raises TooLarge if Content-Length if over MAX_BODY_LENGTH.
    If Content-Length is not set, reads at most MAX_BODY_LENGTH bytes.
    """
    try:
      length = int(environ.get('CONTENT_LENGTH') or MAX_BODY_LENGTH)
    except ValueError:
      raise BadRequest('Invalid Content-Length')
    if length > MAX_BODY_LENGTH:
      raise TooLarge('Content-Length limit exceeded')
    return environ['wsgi.input'].read(length)

  def _authenticate(self, environ, header_list):
    """
    Verify user authentication.

    Raises NotFound if authentication does not pass checks.
    On success, appends a "Cache-Control" header.
    """
    try:
      ca_list = self._cau.getCACertificateList()
      utils.load_certificate(
        environ.get('SSL_CLIENT_CERT', b''),
        trusted_cert_list=ca_list,
        crl=utils.load_crl(
          self._cau.getCertificateRevocationList(),
          ca_list,
        ),
      )
    except (exceptions.CertificateVerificationError, ValueError):
      raise SSLUnauthorized
    header_list.append(('Cache-Control', 'private'))

  def _readJSON(self, environ):
    """
    Read request body and convert to json object.

    Raises BadRequest if request Content-Type is not 'application/json', or if
    json decoding fails.
    """
    if environ.get('CONTENT_TYPE') != 'application/json':
      raise BadRequest('Bad Content-Type')
    data = self._read(environ)
    try:
      return json.loads(data)
    except ValueError:
      raise BadRequest('Invalid json')

  def getCertificateRevocationList(
    self,
    context,
    environ,
  ): # pylint: disable=unused-argument
    """
    Handle GET /{context}/crl .
    """
    return self._returnFile(
      context.getCertificateRevocationList(),
      'application/pkix-crl',
    )

  def getCSR(self, context, environ, subpath):
    """
    Handle GET /{context}/csr/{csr_id} and GET /{context}/csr.
    """
    if subpath:
      return self._returnFile(
        context.getCertificateSigningRequest(self._getCSRID(subpath)),
        'application/pkcs10',
      )
    header_list = []
    self._authenticate(environ, header_list)
    return self._returnFile(
      json.dumps(context.getCertificateRequestList()),
      'application/json',
      header_list,
    )

  def createCertificateSigningRequest(self, context, environ):
    """
    Handle PUT /{context}/csr .
    """
    try:
      csr_id = context.appendCertificateSigningRequest(self._read(environ))
    except exceptions.NotACertificateSigningRequest:
      raise BadRequest('Not a valid certificate signing request')
    return (STATUS_CREATED, [('Location', str(csr_id))], [])

  def deletePendingCertificateRequest(self, context, environ, subpath):
    """
    Handle DELETE /{context}/csr/{csr_id} .
    """
    # Note: single-use variable to verify subpath before allocating more
    # resources to this request
    csr_id = self._getCSRID(subpath)
    header_list = []
    self._authenticate(environ, header_list)
    try:
      context.deletePendingCertificateSigningRequest(csr_id)
    except exceptions.NotFound:
      raise NotFound
    return (STATUS_NO_CONTENT, header_list, [])

  def getCACertificate(
    self,
    context,
    environ,
  ): # pylint: disable=unused-argument
    """
    Handle GET /{context}/crt/ca.crt.pem urls.
    """
    return self._returnFile(
      context.getCACertificate(),
      'application/x-x509-ca-cert',
    )

  def getCACertificateChain(
    self,
    context,
    environ,
  ): # pylint: disable=unused-argument
    """
    Handle GET /{context}/crt/ca.crt.json urls.
    """
    return self._returnFile(
      json.dumps(context.getValidCACertificateChain()),
      'application/json',
    )

  def getCertificate(
    self,
    context,
    environ,
    subpath,
  ): # pylint: disable=unused-argument
    """
    Handle GET /{context}/crt/{crt_id} urls.
    """
    return self._returnFile(
      context.getCertificate(self._getCSRID(subpath)),
      'application/pkix-cert',
    )

  def revokeCertificate(self, context, environ):
    """
    Handle PUT /{context}/crt/revoke .
    """
    header_list = []
    data = self._readJSON(environ)
    if data['digest'] is None:
      self._authenticate(environ, header_list)
      payload = utils.nullUnwrap(data)
      if 'revoke_crt_pem' not in payload:
        context.revokeSerial(payload['revoke_serial'])
        return (STATUS_NO_CONTENT, header_list, [])
    else:
      payload = utils.unwrap(
        data,
        lambda x: x['revoke_crt_pem'],
        context.digest_list,
      )
    context.revoke(
      crt_pem=payload['revoke_crt_pem'].encode('ascii'),
    )
    return (STATUS_NO_CONTENT, header_list, [])

  def renewCertificate(self, context, environ):
    """
    Handle PUT /{context}/crt/renew .
    """
    payload = utils.unwrap(
      self._readJSON(environ),
      lambda x: x['crt_pem'],
      context.digest_list,
    )
    return self._returnFile(
      context.renew(
        crt_pem=payload['crt_pem'].encode('ascii'),
        csr_pem=payload['renew_csr_pem'].encode('ascii'),
      ),
      'application/pkix-cert',
    )

  def createCertificate(self, context, environ, subpath):
    """
    Handle PUT /{context}/crt/{crt_id} urls.
    """
    # Note: single-use variable to verify subpath before allocating more
    # resources to this request
    crt_id = self._getCSRID(subpath)
    body = self._read(environ)
    if not body:
      template_csr = None
    elif environ.get('CONTENT_TYPE') == 'application/pkcs10':
      template_csr = utils.load_certificate_request(body)
    else:
      raise BadRequest('Bad Content-Type')
    header_list = []
    self._authenticate(environ, header_list)
    context.createCertificate(
      csr_id=crt_id,
      template_csr=template_csr,
    )
    return (STATUS_NO_CONTENT, header_list, [])
