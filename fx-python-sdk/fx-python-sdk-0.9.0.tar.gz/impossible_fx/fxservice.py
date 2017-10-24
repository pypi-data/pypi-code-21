"""
	Service Base class for Impossible FX API
"""

import pprint
import requests


class FXError( RuntimeError ):
	"""Base for FX Errors"""
	pass


class FXInternalError( FXError ):
	"""FX Internal Error"""
	pass


class FXNotImplemented( FXError ):
	"""FX Not Implemented"""
	pass


class FXConnectionError( FXError ):
	"""FX Connection Error"""
	pass


class FXServiceError( FXError ):
	"""Base for FX Service Errors"""
	pass


class FXUnauthorized( FXServiceError ):
	"""FX Unauthorized Error
	e.g. no or wrong credentials"""
	pass


class FXNotFound( FXServiceError ):
	"""FX Not Found Error
	e.g. project or asset not found"""
	pass


class FXNotAllowed( FXServiceError ):
	"""FX Not Allowed Error
	e.g. method not allowed"""
	pass


class FXBadRequestError( FXServiceError ):
	"""FX Bad Request Error
	e.g. "SDL program rejected" """
	pass


class FXServerError( FXServiceError ):
	"""FX Server Error
	unexpected Error from Server"""
	pass


class FXGatewayTimeout( FXServerError ):
	"""FX GatewayTimeout"""
	pass


class FXResponseError( FXServerError ):
	"""FX Response Error
	e.g. missing field in response"""
	pass


STATUS_EXCEPTIONS = {
	400:	FXBadRequestError,
	401:	FXUnauthorized,
	404:	FXNotFound,
	405:	FXNotAllowed,
	500:	FXServerError,
	504:	FXGatewayTimeout,
}


class FXService:
	"""
		Base class for Impossible FX API requests
	"""

	def __init__( self,
		region,
		response_timeout,
		max_retries,
		auth,
		**kwargs	# internal use, e.g. debug=True
	):
		self.config = dict(
			region=region,
			protocol="https",
			responseTimeout=response_timeout,
			maxRetries=max_retries,
			auth=auth
		)
		self.config.update( kwargs )
		if self.config.get( "debug" ):
			print "FXService.config:"
			pprint.pprint( self.config )


	def _get_url( self, path ):
		return self.config["protocol"] + "://" + self.config["endpoint_mask"].format( region=self.config["region"] ) + path


	def get_param_or_config( self, params, name ):
		"""get param or config for 'name'"""

		if name in params:
			return params[name]

		return self.config[name]


	def request( self, method, path, data=None, stream=False, headers=None ):
		url = self._get_url( path )
		retry = self.config["maxRetries"] + 1

		while retry:
			retry -= 1
			try:
				if self.config.get( "debug" ):
					print "%s %s" % (method, url)
					if data and hasattr( data, "__getitem__" ):
						print "     data: %s" % data[:200]
					if headers:
						print "  headers: %s" % headers

				response = requests.request( method, url, data=data, stream=stream, headers=headers,
											 auth=self.config["auth"], timeout=self.config["responseTimeout"]/1000.0 )
				break

			except requests.RequestException as exc: # fixme: which exceptions exactly?
				if not retry:
					raise FXConnectionError( exc )

				if self.config.get( "debug" ):
					print "retries left: %d" % retry

		# noinspection PyUnboundLocalVariable
		if not response.ok:
			if self.config.get( "debug" ):
				print "response.content:", response.content

			if response.status_code in STATUS_EXCEPTIONS and response.headers.get( "Content-Type" ) == "application/json":
			# probably nice service related response with "Message" and "Project-UID"

				try:
					json_dict = response.json()
					message = json_dict.get( "Message" )
					project_id = json_dict.get( "Project-UID" )

					if message:
						if project_id:
							exc_message = '"%s %s" -> "%s" for Project ID "%s". Additional info: %s' % (
											method, url, message, project_id, response.content)
						else:
							exc_message = '"%s %s" -> "%s". Additional info: %s' % (
											method, url, project_id, response.content)
						raise STATUS_EXCEPTIONS[response.status_code]( exc_message )
					else:
						pass # let response.raise_for_status() do the work

				except ValueError: # probably json error
					pass # let response.raise_for_status() do the work


			response.raise_for_status()

		return response
