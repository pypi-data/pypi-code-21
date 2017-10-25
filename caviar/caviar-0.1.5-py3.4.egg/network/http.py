#
# This file is part of CAVIAR.
#
# CAVIAR is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CAVIAR is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CAVIAR.  If not, see <http://www.gnu.org/licenses/>.
#

"""
HTTP module.
"""

import requests
import urllib.parse

class HTTPResource:

	"""
	An HTTP resource.
	
	:param list path:
	   List of path components.
	:param str protocol:
	   HTTP protocol, such as 'http' and 'https'.
	:param str host:
	   Host.
	:param str port:
	   Port.
	:param auth:
	   Authentication specification.
	:param dict headers:
	   Common headers. Each entry contains a list of values. 
	"""
	
	def __init__(self, path, protocol, host, port, auth=None, headers=None):
		
		self.__path = path
		self.__protocol = protocol
		self.__host = host
		self.__port = port
		self.__auth = auth or HTTPNoneAuth()
		self.__headers = headers or {}
		
	# TODO Test coverage
	def request(self, method_name):
	
		return HTTPRequest(
			method_name,
			self.__protocol,
			self.__host,
			self.__port,
			self.__path,
			self.__auth,
			self.__headers
		)
		
	# TODO Test coverage
	def push(self, name):
	
		path = []
		path.extend(self.__path)
		path.append(name)
		return HTTPResource(
			path,
			self.__protocol,
			self.__host,
			self.__port,
			self.__auth,
			self.__headers
		)
		
	# TODO Test coverage
	def ref(self, url):
	
		url_obj = urllib.parse.urlparse(url)
		return HTTPResource(
			[
				url_comp
				for url_comp in url_obj.path.split("/")
				if len(url_comp) > 0
			],
			url_obj.scheme,
			url_obj.hostname,
			url_obj.port,
			self.__auth,
			self.__headers
		)
		
# TODO Test coverage
class HTTPRequest:

	def __init__(self, method, protocol, host, port, path, auth, headers):
	
		self.__method = method
		self.__path = "/".join(path)
		
		self.__url = "{}://{}:{}/{}".format(
			protocol,
			host,
			port,
			self.__path
		)
		self.__requests_method = getattr(requests, self.__method.lower())
		self.__auth = auth.translate()
		self.__headers = headers
		self.__query = {}
		self.__data = {}
		self.__files = {}
		
	# TODO Test coverage
	@property
	def method(self):
	
		return self.__method
		
	# TODO Test coverage
	@property
	def path(self):
	
		return "/{}".format(self.__path)
		
	# TODO Test coverage
	def query_param(self, name, value):
	
		self.__query[name] = value
		
	# TODO Test coverage
	def data_param(self, name, value):
	
		self.__data[name] = value
		
	# TODO Test coverage
	def file_param(self, name, value):
	
		self.__files[name] = value
		
	# TODO Test coverage
	def perform(self):
	
		headers = {}
		headers.update(self.__headers)
		headers.update({
			"Accept": [ "application/json" ]
		})
		resp = self.__requests_method(
			url=self.__url,
			auth=self.__auth,
			headers={
				name: ", ".join(value)
				for name, value
				in headers.items()
			},
			params=self.__query,
			data=self.__data,
			files=self.__files,
			verify=False
		)
		try:
			content = resp.json()
		except ValueError:
			content = None
		return HTTPResponse(
			resp.status_code,
			{
				name: value.split("\\s,")
				for name, value
				in resp.headers.items()
			},
			content
		)
		
class HTTPResponse:

	"""
	HTTP response attributes.
	
	:param int status_code:
	   Response status code.
	:param dict headers:
	   Dictionary with lists of strings containing response headers.
	:param dict content:
	   Dictionary that comes from decoding the JSON response body.
	"""
	
	def __init__(self, status_code, headers, content):
	
		self.__status_code = status_code
		self.__headers = headers
		self.__content = content
		
	@property
	def status_code(self):
	
		"""
		Response status code.
		
		:rtype:
		   int
		:return:
		   Status code value.
		"""
		
		return self.__status_code
		
	@property
	def headers(self):
	
		"""
		Dictionary with lists of strings containing response headers.
		
		:rtype:
		   dict
		:return:
		   Headers dictionary.
		"""
		
		return self.__headers
		
	@property
	def content(self):
	
		"""
		Dictionary that comes from decoding the JSON response body.
		
		:rtype:
		   dict
		:return:
		   Content dictionary.
		"""
		
		return self.__content
			
class HTTPNoneAuth:

	"""
	No authentication.
	"""
	
	def translate(self):
	
		"""
		Translate it to the underlying implementation authentication.
		
		:return:
		   Translated authentication.
		"""
		
		return None
		
class HTTPBasicAuth:

	"""
	Basic authentication.
	
	:param str user:
	   User name.
	:param str password:
	   User password.
	"""
	
	def __init__(self, user, password):
	
		self.__user = user
		self.__password = password
		
	def translate(self):
	
		"""
		Translate it to the underlying implementation authentication.
		
		:return:
		   Translated authentication.
		"""
		
		return requests.auth.HTTPBasicAuth(
			self.__user,
			self.__password
		)

