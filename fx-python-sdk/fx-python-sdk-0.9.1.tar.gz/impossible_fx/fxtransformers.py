"""
	result Transformers for Impossible FX API
"""

import datetime

try:
	from . import Movie_pb2 as proto
except Exception:
	print 'Cannot import "Movie_pb2", movies will be blobs.'
	proto = None

import fxutils
import fxservice


def TransformProjectList( service, _input, response ):
	import project_types

	json_dict = response.json()
	additional = {"region": service.config["region"]}

	projects = [project_types.Project( fxutils.update( data, additional ) )
					for data in json_dict["Metadata"].values()]

	for project in projects:
		fxutils.mixin_service( project, service, "project_id" )

	return projects


def TransformProjectGet( service, _input, response ):
	"""get one project from project list"""
	import project_types

	json_dict = response.json()
	project_id = _input["project_id"]
	additional = {"region": service.config["region"]}
	metadata = json_dict["Metadata"]
	if project_id in metadata:
		project = project_types.Project( fxutils.update( metadata[project_id], additional ) )
	else:
		raise fxservice.FXNotFound( "Project not found: %s" % project_id )

	fxutils.mixin_service( project, service, "project_id" )

	return project


def TransformAssetList( service, _input, response ):
	import fxtypes
	import project_types

	json_dict = response.json()
	additional = {
		"region": service.config["region"],
		"project_id": _input["project_id"]
	}

	sounds = [project_types.Sound( fxutils.update( data, additional ) )
			  			for data in [json_dict["Metadata"][name]
							for name in json_dict["Audios"]]]

	videos = [project_types.Video( fxutils.update( data, additional ) )
			  			for data in [json_dict["Metadata"][name]
							for name in json_dict["Videos"]]]

	images = [project_types.Image( fxutils.update( data, additional ) )
			  			for data in [json_dict["Metadata"][name]
							for name in json_dict["Images"]]]

	fonts = [project_types.Font( fxutils.update( data, additional ) )
			  			for data in [json_dict["Metadata"][name]
							for name in json_dict["Fonts"]]]

	datasources = [project_types.Datasource( fxutils.update( data, additional ) )
			  			for data in [json_dict["Metadata"][name]
							for name in json_dict["Datasources"]]]

	aux = [project_types.AuxData( fxutils.update( data, additional ) )
			  			for data in [json_dict["Metadata"][name]
							for name in json_dict["Generic"]]]

	# FIXME: Name 'AuxData' but 'Trackdata'?
	if "Trackdata" in json_dict: # FIXME: Trackdata is not part of list_assets yet?!
		trackdata = [project_types.Trackdata( fxutils.update( data, additional ) )
							for data in [json_dict["Metadata"][name]
								for name in json_dict["Trackdata"]]]
	else:
		trackdata = []

	all = {value.name: value for value in sounds + videos + images + fonts + datasources + trackdata + aux }

	return fxtypes.Assets(
		all=all,
		sounds=sounds,
		videos=videos,
		images=images,
		fonts=fonts,
		datasources=datasources,
		aux=aux,
		trackdata=trackdata,
	)


def TransformProjectCreate( service, _input, response ):
	import project_types

	json_dict = response.json()
	# fake 'Project' members we're not getting from the response
	json_dict["region"] = service.config["region"]
	json_dict["name"] = _input["name"]
	json_dict["date_created"] = datetime.datetime.now()
	json_dict["migrated"] = []
	json_dict["uid"] = json_dict["Project-UID"]

	project = project_types.Project( json_dict )
	fxutils.mixin_service( project, service, "project_id" )

	return project


def TransformAssetGet( service, _input, response ):
	return response.raw


def TransformTokenGet( service, _input, response ):
	import render_types
	return render_types.TokenURL( response.json() )

def TransformTokenUpload( service, _input, response ):
	import render_types
	return render_types.TokenUpload( response.json() )


def _computeRenderURL( endpoint, mode, format, token ) :
	return endpoint+ "/v2/" + mode + "/" + token + "." + format


def TransformRenderURL( service, _input, response ):
	import render_types

	json_dict = response.json()

	result = render_types.TokenURL( {
		"Token": json_dict["token"],
		"URL": _computeRenderURL( service.get_param_or_config( _input, "endpoint" ),
								   _input["mode"],
								   _input["format"],
								   json_dict["token"] )
		} )

	return result


def TransformMovieGet( service, _input, response ):
	if proto is None:
		return  response.content

	movie = proto.Movie()
	movie.ParseFromString( response.content )
	return movie

