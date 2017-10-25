"""
Result types for Impossible FX Render API

Please send suggestions and bug reports to:
python-sdk@impossiblesoftware.com
"""

import fxservice
import fxconverters


class Token:

	def __init__( self, data ):
		"""
		:param data: data dictionary. Usually FX API server response as JSON dictionary
		:raise fxservice.FXError: thrown if expected response fields are missing or another exception occurred

		Members: 

		- str token: 
		"""
		try:
			self.token = data["Token"]
		except KeyError as detail:
			raise fxservice.FXResponseError( 'Token: missing field "%s" in server response %s' % (detail.args[0], repr( data )) )
		except (ValueError, TypeError) as detail:
			raise fxservice.FXResponseError( 'Token: "%s" for server response %s' % (detail.args[0], repr( data )) )
		except Exception as detail:
			raise fxservice.FXInternalError( 'Token: "%s" for server response %s' % (detail.args[0], repr( data )) )


	def __repr__( self ):
		return 'Token( {"token": %s} )' % (
			repr( self.token ) )


class TokenUpload:

	def __init__( self, data ):
		"""
		:param data: data dictionary. Usually FX API server response as JSON dictionary
		:raise fxservice.FXError: thrown if expected response fields are missing or another exception occurred

		Members: 

		- str token: 
		- str upload: 
		"""
		try:
			self.token = data["token"]
			self.upload = data["upload"]
		except KeyError as detail:
			raise fxservice.FXResponseError( 'TokenUpload: missing field "%s" in server response %s' % (detail.args[0], repr( data )) )
		except (ValueError, TypeError) as detail:
			raise fxservice.FXResponseError( 'TokenUpload: "%s" for server response %s' % (detail.args[0], repr( data )) )
		except Exception as detail:
			raise fxservice.FXInternalError( 'TokenUpload: "%s" for server response %s' % (detail.args[0], repr( data )) )


	def __repr__( self ):
		return 'TokenUpload( {"token": %s, "upload": %s} )' % (
			repr( self.token ),
			repr( self.upload ) )


class TokenURL:

	def __init__( self, data ):
		"""
		:param data: data dictionary. Usually FX API server response as JSON dictionary
		:raise fxservice.FXError: thrown if expected response fields are missing or another exception occurred

		Members: 

		- str token: Render token
		- str url: URL to render the video
		"""
		try:
			self.token = data["Token"] # Render token
			self.url = data["URL"] # URL to render the video
		except KeyError as detail:
			raise fxservice.FXResponseError( 'TokenURL: missing field "%s" in server response %s' % (detail.args[0], repr( data )) )
		except (ValueError, TypeError) as detail:
			raise fxservice.FXResponseError( 'TokenURL: "%s" for server response %s' % (detail.args[0], repr( data )) )
		except Exception as detail:
			raise fxservice.FXInternalError( 'TokenURL: "%s" for server response %s' % (detail.args[0], repr( data )) )


	def __repr__( self ):
		return 'TokenURL( {"token": %s, "url": %s} )' % (
			repr( self.token ),
			repr( self.url ) )
