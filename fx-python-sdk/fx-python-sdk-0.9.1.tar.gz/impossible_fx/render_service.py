"""
Impossible FX Render API

Please send suggestions and bug reports to:
python-sdk@impossiblesoftware.com
"""

import json
import copy

from .fxservice import FXService
from . import fxutils
from . import fxtransformers

globalEndpoint = 'render.impossible.io'


class RenderService( FXService ):

	def __init__( self,
		region=None,
		response_timeout=600000,
		max_retries=10,
		auth=None,
		**kwargs	# internal use, e.g. debug=True
	):
		"""
		:param region: 		Region for requests
		:type region:		str

		:param response_timeout:	Response timeout for requests in milliseconds
		:type response_timeout:	int

		:param max_retries:	maximum number of retries for failed connections
		:type max_retries:	int

		:param auth:		API key and API secret, required for ProjectService, not for RenderService
		:type auth:			tuple of strings
		"""

		FXService.__init__( self, region, response_timeout, max_retries, auth, **kwargs )
		if region is None:
		    if globalEndpoint is None:
		        raise ValueError, "This service requires a specific region"
		    self.config["endpoint_mask"] = "'render.impossible.io'".replace("'", "")
		else:
			self.config["endpoint_mask"] = "render-{region}.impossible.io"


	def get_token( self, project_id, movie_name, params ) :
		"""
		GetToken: Create a render token

		:param project_id: A Project ID (required)
		:type project_id: str

		:param movie_name: Movie to render (required)
		:type movie_name: str

		:param params: Render Parameters (required)
		:type params: dict
		"""
		_input = {'project_id': project_id, 'movie_name': movie_name, 'params': params}
		path = "/v2/render/{prjuid}".format( prjuid=project_id )
		data = json.dumps( {
			"movie": movie_name,
			"params": params,
		} )
		result = self.request( "POST", path, data, stream=False, headers={"Content-Type": "application/json"} )
		result = fxtransformers.TransformTokenGet( self, _input, result )
		return result


	def get_render_url( self, project_id, movie_name, params, endpoint='https://render.impossible.io', mode='render', format='mp4' ) :
		"""
		GetRenderURL: Create a render URL

		:param project_id: A Project ID (required)
		:type project_id: str

		:param movie_name: Movie to render (required)
		:type movie_name: str

		:param params: Render Parameters (required)
		:type params: dict

		:param endpoint: Render Endpoint (default: 'https://render.impossible.io')
		:type endpoint: str

		:param mode: Render Mode (default: 'render')
		:type mode: str

		:param format: Format of video (default: 'mp4')
		:type format: str
		"""
		_input = {'project_id': project_id, 'movie_name': movie_name, 'params': params, 'endpoint': endpoint, 'mode': mode, 'format': format}
		path = "/v2/render/{prjuid}".format( prjuid=project_id )
		data = json.dumps( {
			"movie": movie_name,
			"params": params,
		} )
		result = self.request( "POST", path, data, stream=False, headers={"Content-Type": "application/json"} )
		result = fxtransformers.TransformRenderURL( self, _input, result )
		return result


	def get_poster_frame_url( self, project_id, movie_name, params, frame, endpoint='https://render.impossible.io', mode='render', format='jpg' ) :
		"""
		GetPosterFrameURL: Create a render URL

		:param project_id: A Project ID (required)
		:type project_id: str

		:param movie_name: Movie to render (required)
		:type movie_name: str

		:param params: Render Parameters (required)
		:type params: dict

		:param frame: Frame Number (required)
		:type frame: int

		:param endpoint: Render Endpoint (default: 'https://render.impossible.io')
		:type endpoint: str

		:param mode: Render Mode (default: 'render')
		:type mode: str

		:param format: Format of image (jpg|png) (default: 'jpg')
		:type format: str
		"""
		_input = {'project_id': project_id, 'movie_name': movie_name, 'params': params, 'frame': frame, 'endpoint': endpoint, 'mode': mode, 'format': format}
		path = "/v2/render/{prjuid}".format( prjuid=project_id )
		params = copy.deepcopy( params )
		fxutils.deep_set( params, ['frame'], frame )
		data = json.dumps( {
			"movie": movie_name,
			"params": params,
		} )
		result = self.request( "POST", path, data, stream=False, headers={"Content-Type": "application/json"} )
		result = fxtransformers.TransformRenderURL( self, _input, result )
		return result


	def render_to_s3( self, project_id, movie_name, params, format, bucket, filename, type='s3', async=None, use_policy=None, access_key_id=None, secret_access_key=None, content_type=None, content_disposition=None, acl=None, cache_control=None, secure=None, s3_host=None, reduced_redundancy=None ) :
		"""
		RenderToS3: This operation renders a video and uploads the file to Amazon S3

		:param project_id: A Project ID (required)
		:type project_id: str

		:param movie_name: Movie to render (required)
		:type movie_name: str

		:param params: Render Parameters (required)
		:type params: dict

		:param format: Format to Render (required)
		:type format: str

		:param bucket: S3 Bucket Name (required)
		:type bucket: str

		:param filename: S3 Filename (required)
		:type filename: str

		:param type:  (default: 's3')
		:type type: str

		:param async: Perform Async (optional)
		:type async: boolean

		:param use_policy: Use S3 Bucket Policy instead of AccessKey/SecretAccessKey (optional)
		:type use_policy: boolean

		:param access_key_id: AWS Access Key ID (optional)
		:type access_key_id: str

		:param secret_access_key: AWS Secret Access Key (optional)
		:type secret_access_key: str

		:param content_type: CMediatype (MIME) for the destination object (optional)
		:type content_type: str

		:param content_disposition: Content disposition type for the destination object (optional)
		:type content_disposition: str

		:param acl: Access Control for the destination object. Can be one of: private | public-read | public-read-write | authenticated-read (optional)
		:type acl: str

		:param cache_control: Extra controls for the "Cache-Control"-header (optional)
		:type cache_control: str

		:param secure: Return HTTPS URLs for Object URL (optional)
		:type secure: boolean

		:param s3_host: For Signature V4 regions (e.g. eu-central-1), the S3 endpoint is required. (optional)
		:type s3_host: str

		:param reduced_redundancy: Use reduced redundancy for the destination object. (optional)
		:type reduced_redundancy: boolean
		"""
		_input = {'project_id': project_id, 'movie_name': movie_name, 'params': params, 'format': format, 'bucket': bucket, 'filename': filename, 'type': type, 'async': async, 'use_policy': use_policy, 'access_key_id': access_key_id, 'secret_access_key': secret_access_key, 'content_type': content_type, 'content_disposition': content_disposition, 'acl': acl, 'cache_control': cache_control, 'secure': secure, 's3_host': s3_host, 'reduced_redundancy': reduced_redundancy}
		path = "/v2/render/{prjuid}".format( prjuid=project_id )
		upload = {}
		fxutils.deep_set( upload, ['extension'], format )
		fxutils.deep_set( upload, ['destination', 'bucket'], bucket )
		fxutils.deep_set( upload, ['destination', 'filename'], filename )
		fxutils.deep_set( upload, ['destination', 'type'], type )
		fxutils.deep_set( upload, ['async'], async )
		fxutils.deep_set( upload, ['destination', 'aws_use_policy'], use_policy )
		fxutils.deep_set( upload, ['destination', 'aws_access_key_id'], access_key_id )
		fxutils.deep_set( upload, ['destination', 'aws_secret_access_key'], secret_access_key )
		fxutils.deep_set( upload, ['destination', 'contenttype'], content_type )
		fxutils.deep_set( upload, ['destination', 'contentdisposition'], content_disposition )
		fxutils.deep_set( upload, ['destination', 'acl'], acl )
		fxutils.deep_set( upload, ['destination', 'cachecontrol'], cache_control )
		fxutils.deep_set( upload, ['destination', 'secure'], secure )
		fxutils.deep_set( upload, ['destination', 's3host'], s3_host )
		fxutils.deep_set( upload, ['destination', 'reduced_redundancy'], reduced_redundancy )
		data = json.dumps( {
			"movie": movie_name,
			"params": params,
			"upload": upload,
		} )
		result = self.request( "POST", path, data, stream=False, headers={"Content-Type": "application/json"} )
		result = fxtransformers.TransformTokenUpload( self, _input, result )
		return result


	def render_to_azure( self, project_id, movie_name, params, format, account, container, key, type='azureblob', async=None, content_type=None ) :
		"""
		RenderToAzure: This operation renders a video and uploads the file to Microsoft Azure Blob Storage

		:param project_id: A Project ID (required)
		:type project_id: str

		:param movie_name: Movie to render (required)
		:type movie_name: str

		:param params: Render Parameters (required)
		:type params: dict

		:param format: Format to Render (required)
		:type format: str

		:param account: Storage account name (required)
		:type account: str

		:param container: Name of storage container (required)
		:type container: str

		:param key: Filename for the destination object (required)
		:type key: str

		:param type:  (default: 'azureblob')
		:type type: str

		:param async: Perform Async (optional)
		:type async: boolean

		:param content_type: Mediatype (MIME) for the destination object (optional)
		:type content_type: str
		"""
		_input = {'project_id': project_id, 'movie_name': movie_name, 'params': params, 'format': format, 'account': account, 'container': container, 'key': key, 'type': type, 'async': async, 'content_type': content_type}
		path = "/v2/render/{prjuid}".format( prjuid=project_id )
		upload = {}
		fxutils.deep_set( upload, ['extension'], format )
		fxutils.deep_set( upload, ['destination', 'account'], account )
		fxutils.deep_set( upload, ['destination', 'container'], container )
		fxutils.deep_set( upload, ['destination', 'key'], key )
		fxutils.deep_set( upload, ['destination', 'type'], type )
		fxutils.deep_set( upload, ['async'], async )
		fxutils.deep_set( upload, ['destination', 'contenttype'], content_type )
		data = json.dumps( {
			"movie": movie_name,
			"params": params,
			"upload": upload,
		} )
		result = self.request( "POST", path, data, stream=False, headers={"Content-Type": "application/json"} )
		result = fxtransformers.TransformTokenUpload( self, _input, result )
		return result


	def render_to_youtube( self, project_id, movie_name, params, format, title, description, category, type='youtube', async=None, o_auth_access_token=None, auth_secret=None, status=None, tags=None, playlist_id=None, notify_subscribers=None ) :
		"""
		RenderToYoutube: This operation renders a video and uploads the video to Youtube

		:param project_id: A Project ID (required)
		:type project_id: str

		:param movie_name: Movie to render (required)
		:type movie_name: str

		:param params: Render Parameters (required)
		:type params: dict

		:param format: Format to Render (required)
		:type format: str

		:param title: Video title (required)
		:type title: str

		:param description: Video description (required)
		:type description: str

		:param category: Numerical ID for category. See List of <a href=" https://www.impossiblesoftware.com/docs/rendering/uploading/youtube.html#categories">Youtube Categories</a> (required)
		:type category: str

		:param type:  (default: 'youtube')
		:type type: str

		:param async: Perform Async (optional)
		:type async: boolean

		:param o_auth_access_token: Youtube OAuth 2.0 access token (optional)
		:type o_auth_access_token: str

		:param auth_secret: ImpossibleFX auth secret (optional)
		:type auth_secret: str

		:param status: One of "private", "public", "unlisted" (optional)
		:type status: str

		:param tags: Tags, e.g. ["tag1", "tag2"] (optional)
		:type tags: list

		:param playlist_id: Add video to playlist (playlistID, not name!) (optional)
		:type playlist_id: str

		:param notify_subscribers: Notify Subscribers (default: false) (optional)
		:type notify_subscribers: boolean
		"""
		_input = {'project_id': project_id, 'movie_name': movie_name, 'params': params, 'format': format, 'title': title, 'description': description, 'category': category, 'type': type, 'async': async, 'o_auth_access_token': o_auth_access_token, 'auth_secret': auth_secret, 'status': status, 'tags': tags, 'playlist_id': playlist_id, 'notify_subscribers': notify_subscribers}
		path = "/v2/render/{prjuid}".format( prjuid=project_id )
		upload = {}
		fxutils.deep_set( upload, ['extension'], format )
		fxutils.deep_set( upload, ['destination', 'title'], title )
		fxutils.deep_set( upload, ['destination', 'description'], description )
		fxutils.deep_set( upload, ['destination', 'category'], category )
		fxutils.deep_set( upload, ['destination', 'type'], type )
		fxutils.deep_set( upload, ['async'], async )
		fxutils.deep_set( upload, ['destination', 'account'], o_auth_access_token )
		fxutils.deep_set( upload, ['destination', 'container'], auth_secret )
		fxutils.deep_set( upload, ['destination', 'status'], status )
		fxutils.deep_set( upload, ['destination', 'tags'], tags )
		fxutils.deep_set( upload, ['destination', 'playlistid'], playlist_id )
		fxutils.deep_set( upload, ['destination', 'notifysubscribers'], notify_subscribers )
		data = json.dumps( {
			"movie": movie_name,
			"params": params,
			"upload": upload,
		} )
		result = self.request( "POST", path, data, stream=False, headers={"Content-Type": "application/json"} )
		result = fxtransformers.TransformTokenUpload( self, _input, result )
		return result


	def render_to_facebook( self, project_id, movie_name, params, format, o_auth_access_token, type='facebook', async=None, title=None, description=None, caption=None, name=None ) :
		"""
		RenderToFacebook: This operation renders a video and uploads the video to Facebook

		:param project_id: A Project ID (required)
		:type project_id: str

		:param movie_name: Movie to render (required)
		:type movie_name: str

		:param params: Render Parameters (required)
		:type params: dict

		:param format: Format to Render (required)
		:type format: str

		:param o_auth_access_token: Facebook OAuth 2.0 access token (required)
		:type o_auth_access_token: str

		:param type:  (default: 'facebook')
		:type type: str

		:param async: Perform Async (optional)
		:type async: boolean

		:param title: Video title (optional)
		:type title: str

		:param description: Video description (optional)
		:type description: str

		:param caption: Video caption (optional)
		:type caption: str

		:param name: Video name (optional)
		:type name: str
		"""
		_input = {'project_id': project_id, 'movie_name': movie_name, 'params': params, 'format': format, 'o_auth_access_token': o_auth_access_token, 'type': type, 'async': async, 'title': title, 'description': description, 'caption': caption, 'name': name}
		path = "/v2/render/{prjuid}".format( prjuid=project_id )
		upload = {}
		fxutils.deep_set( upload, ['extension'], format )
		fxutils.deep_set( upload, ['destination', 'account'], o_auth_access_token )
		fxutils.deep_set( upload, ['destination', 'type'], type )
		fxutils.deep_set( upload, ['async'], async )
		fxutils.deep_set( upload, ['destination', 'title'], title )
		fxutils.deep_set( upload, ['destination', 'description'], description )
		fxutils.deep_set( upload, ['destination', 'caption'], caption )
		fxutils.deep_set( upload, ['destination', 'name'], name )
		data = json.dumps( {
			"movie": movie_name,
			"params": params,
			"upload": upload,
		} )
		result = self.request( "POST", path, data, stream=False, headers={"Content-Type": "application/json"} )
		result = fxtransformers.TransformTokenUpload( self, _input, result )
		return result


	def render_to_dropbox( self, project_id, movie_name, params, format, o_auth_access_token, auth_secret, filename, type='facebook', async=None ) :
		"""
		RenderToDropbox: This operation renders a video and uploads the video to Dropbox

		:param project_id: A Project ID (required)
		:type project_id: str

		:param movie_name: Movie to render (required)
		:type movie_name: str

		:param params: Render Parameters (required)
		:type params: dict

		:param format: Format to Render (required)
		:type format: str

		:param o_auth_access_token: Facebook OAuth 2.0 access token (required)
		:type o_auth_access_token: str

		:param auth_secret: Impossible FX auth secret (required)
		:type auth_secret: str

		:param filename: Filename for uploaded video (required)
		:type filename: str

		:param type:  (default: 'facebook')
		:type type: str

		:param async: Perform Async (optional)
		:type async: boolean
		"""
		_input = {'project_id': project_id, 'movie_name': movie_name, 'params': params, 'format': format, 'o_auth_access_token': o_auth_access_token, 'auth_secret': auth_secret, 'filename': filename, 'type': type, 'async': async}
		path = "/v2/render/{prjuid}".format( prjuid=project_id )
		upload = {}
		fxutils.deep_set( upload, ['extension'], format )
		fxutils.deep_set( upload, ['destination', 'account'], o_auth_access_token )
		fxutils.deep_set( upload, ['destination', 'auth_secret'], auth_secret )
		fxutils.deep_set( upload, ['destination', 'filename'], filename )
		fxutils.deep_set( upload, ['destination', 'type'], type )
		fxutils.deep_set( upload, ['async'], async )
		data = json.dumps( {
			"movie": movie_name,
			"params": params,
			"upload": upload,
		} )
		result = self.request( "POST", path, data, stream=False, headers={"Content-Type": "application/json"} )
		result = fxtransformers.TransformTokenUpload( self, _input, result )
		return result
