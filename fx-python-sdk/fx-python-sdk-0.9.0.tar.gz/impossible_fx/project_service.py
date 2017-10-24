"""
Impossible FX Project API

Please send suggestions and bug reports to:
python-sdk@impossiblesoftware.com
"""

import json
import copy

from .fxservice import FXService
from . import fxutils
from . import fxtransformers

globalEndpoint = None


class ProjectService( FXService ):

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
		    self.config["endpoint_mask"] = "None".replace("'", "")
		else:
			self.config["endpoint_mask"] = "api-{region}.impossible.io"


	def list_projects( self ) :
		"""
		ListProjects: List all projects
		"""
		_input = {}
		path = "/v1/list/project/"
		data = None
		result = self.request( "GET", path, data, stream=False )
		result = fxtransformers.TransformProjectList( self, _input, result )
		return result


	def get_project( self, project_id ) :
		"""
		GetProject: Get a certain project

		:param project_id: The Project ID to get (required)
		:type project_id: str
		"""
		_input = {'project_id': project_id}
		path = "/v1/list/project/"
		data = None
		result = self.request( "GET", path, data, stream=False )
		result = fxtransformers.TransformProjectGet( self, _input, result )
		return result


	def delete_project( self, project_id ) :
		"""
		DeleteProject: Delete a project

		:param project_id: The Project ID to delete (required)
		:type project_id: str
		"""
		_input = {'project_id': project_id}
		path = "/v1/project/{prjuid}".format( prjuid=project_id )
		data = None
		result = self.request( "DELETE", path, data, stream=False )
		return result


	def create_project( self, name ) :
		"""
		CreateProject: Create a project

		:param name: Name of new project (required)
		:type name: str
		"""
		_input = {'name': name}
		path = "/v1/project/{name}".format( name=name )
		data = None
		result = self.request( "POST", path, data, stream=False )
		result = fxtransformers.TransformProjectCreate( self, _input, result )
		return result


	def list_assets( self, project_id ) :
		"""
		ListAssets: List assets in a project

		:param project_id: Project UID (required)
		:type project_id: str
		"""
		_input = {'project_id': project_id}
		path = "/v1/list/data/{prjuid}".format( prjuid=project_id )
		data = None
		result = self.request( "GET", path, data, stream=False )
		result = fxtransformers.TransformAssetList( self, _input, result )
		return result


	def get_asset( self, project_id, name ) :
		"""
		GetAsset: Download asset

		:param project_id: Project UID (required)
		:type project_id: str

		:param name: Asset Identifier (required)
		:type name: str
		"""
		_input = {'project_id': project_id, 'name': name}
		path = "/v1/data/{prjuid}/{name}".format( prjuid=project_id, name=name )
		data = None
		result = self.request( "GET", path, data, stream=True )
		result = fxtransformers.TransformAssetGet( self, _input, result )
		return result


	def upload_asset( self, project_id, name, data ) :
		"""
		UploadAsset: Add a new asset to the project

		:param project_id: Project UID (required)
		:type project_id: str

		:param name: Asset Identifier (required)
		:type name: str

		:param data: Asset data. (required)
		:type data: blob
		"""
		_input = {'project_id': project_id, 'name': name, 'data': data}
		path = "/v1/data/{prjuid}/{name}".format( prjuid=project_id, name=name )
		result = self.request( "POST", path, data, stream=False )
		return result


	def update_asset( self, project_id, name, data ) :
		"""
		UpdateAsset: Add a new asset or update an existing one

		:param project_id: Project UID (required)
		:type project_id: str

		:param name: Asset Identifier (required)
		:type name: str

		:param data: Asset data. Buffer or file-like or generator (required)
		:type data: blob
		"""
		_input = {'project_id': project_id, 'name': name, 'data': data}
		path = "/v1/data/{prjuid}/{name}".format( prjuid=project_id, name=name )
		result = self.request( "PUT", path, data, stream=False )
		return result


	def delete_asset( self, project_id, name ) :
		"""
		DeleteAsset: Delete an asset

		:param project_id: Project UID (required)
		:type project_id: str

		:param name: Asset Identifier (required)
		:type name: str
		"""
		_input = {'project_id': project_id, 'name': name}
		path = "/v1/data/{prjuid}/{name}".format( prjuid=project_id, name=name )
		data = None
		result = self.request( "DELETE", path, data, stream=False )
		return result


	def get_appdata( self, project_id, name ) :
		"""
		GetAppdata: Download app data

		:param project_id: Project UID (required)
		:type project_id: str

		:param name: App data Identifier (required)
		:type name: str
		"""
		_input = {'project_id': project_id, 'name': name}
		path = "/v1/appdata/{prjuid}/{name}".format( prjuid=project_id, name=name )
		data = None
		result = self.request( "GET", path, data, stream=True )
		result = fxtransformers.TransformAssetGet( self, _input, result )
		return result


	def put_appdata( self, project_id, name, data ) :
		"""
		PutAppdata: Add new Appdata or update existing one

		:param project_id: Project UID (required)
		:type project_id: str

		:param name: Appdata Identifier (required)
		:type name: str

		:param data: Appdata data. Buffer or file-like or generator (required)
		:type data: blob
		"""
		_input = {'project_id': project_id, 'name': name, 'data': data}
		path = "/v1/appdata/{prjuid}/{name}".format( prjuid=project_id, name=name )
		result = self.request( "PUT", path, data, stream=False )
		return result


	def delete_appdata( self, project_id, name ) :
		"""
		DeleteAppdata: Delete appdata

		:param project_id: Project UID (required)
		:type project_id: str

		:param name: Appdata Identifier (required)
		:type name: str
		"""
		_input = {'project_id': project_id, 'name': name}
		path = "/v1/appdata/{prjuid}/{name}".format( prjuid=project_id, name=name )
		data = None
		result = self.request( "DELETE", path, data, stream=False )
		return result


	def create_movie( self, project_id, name, movie ) :
		"""
		CreateMovie: Create or update a dynamic movie

		:param project_id: Project UID (required)
		:type project_id: str

		:param name: Movie Identifier (required)
		:type name: str

		:param movie: Movie template (required)
		:type movie: Movie
		"""
		_input = {'project_id': project_id, 'name': name, 'movie': movie}
		path = "/v1/sdl/{prjuid}/{name}".format( prjuid=project_id, name=name )
		data = movie
		data = data.SerializeToString()
		result = self.request( "PUT", path, data, stream=False )
		return result


	def delete_movie( self, project_id, name ) :
		"""
		DeleteMovie: Delete a dynamic movie

		:param project_id: Project UID (required)
		:type project_id: str

		:param name: Movie Identifier (required)
		:type name: str
		"""
		_input = {'project_id': project_id, 'name': name}
		path = "/v1/sdl/{prjuid}/{name}".format( prjuid=project_id, name=name )
		data = None
		result = self.request( "DELETE", path, data, stream=False )
		return result


	def get_movie( self, project_id, name ) :
		"""
		GetMovie: Get Movie (Protobuf)

		:param project_id: Project UID (required)
		:type project_id: str

		:param name: Movie Identifier (required)
		:type name: str
		"""
		_input = {'project_id': project_id, 'name': name}
		path = "/v1/sdl/{prjuid}/{name}".format( prjuid=project_id, name=name )
		data = None
		result = self.request( "GET", path, data, stream=False )
		result = fxtransformers.TransformMovieGet( self, _input, result )
		return result
