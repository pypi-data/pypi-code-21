"""
Result types for Impossible FX Project API

Please send suggestions and bug reports to:
python-sdk@impossiblesoftware.com
"""

import fxservice
import fxconverters


class Project:

	def __init__( self, data ):
		"""
		:param data: data dictionary. Usually FX API server response as JSON dictionary
		:raise fxservice.FXError: thrown if expected response fields are missing or another exception occurred

		Members: 

		- str region: The id of the region for this project
		- str project_id: Project ID
		- str name: Name of the project
		- datetime created: Creation date of project
		- list migrated: 
		"""
		try:
			self.region = data["region"] # The id of the region for this project
			self.project_id = data["uid"] # Project ID
			self.name = data["name"] # Name of the project
			self.created = fxconverters.to_datetime( data["date_created"] ) # Creation date of project
			self.migrated = data["migrated"]
		except KeyError as detail:
			raise fxservice.FXResponseError( 'Project: missing field "%s" in server response %s' % (detail.args[0], repr( data )) )
		except (ValueError, TypeError) as detail:
			raise fxservice.FXResponseError( 'Project: "%s" for server response %s' % (detail.args[0], repr( data )) )
		except Exception as detail:
			raise fxservice.FXInternalError( 'Project: "%s" for server response %s' % (detail.args[0], repr( data )) )


	def __repr__( self ):
		return 'Project( {"region": %s, "project_id": %s, "name": %s, "created": %s, "migrated": %s} )' % (
			repr( self.region ),
			repr( self.project_id ),
			repr( self.name ),
			repr( self.created ),
			repr( self.migrated ) )


class Asset:

	def __init__( self, data ):
		"""
		:param data: data dictionary. Usually FX API server response as JSON dictionary
		:raise fxservice.FXError: thrown if expected response fields are missing or another exception occurred

		Members: 

		- str region: The id of the region for this object
		- str project_id: The project ID this asset belongs to.
		- str name: The name (or filename) of the asset
		- str kind: Type of asset ('video', 'image', ...)
		- datetime created: Creation time of asset
		"""
		try:
			self.region = data["region"] # The id of the region for this object
			self.project_id = data["ProjectId"] # The project ID this asset belongs to.
			self.name = data["Name"] # The name (or filename) of the asset
			self.kind = data["Kind"] # Type of asset ('video', 'image', ...)
			self.created = fxconverters.to_datetime( data["date_created"] ) # Creation time of asset
		except KeyError as detail:
			raise fxservice.FXResponseError( 'Asset: missing field "%s" in server response %s' % (detail.args[0], repr( data )) )
		except (ValueError, TypeError) as detail:
			raise fxservice.FXResponseError( 'Asset: "%s" for server response %s' % (detail.args[0], repr( data )) )
		except Exception as detail:
			raise fxservice.FXInternalError( 'Asset: "%s" for server response %s' % (detail.args[0], repr( data )) )


	def __repr__( self ):
		return 'Asset( {"region": %s, "project_id": %s, "name": %s, "kind": %s, "created": %s} )' % (
			repr( self.region ),
			repr( self.project_id ),
			repr( self.name ),
			repr( self.kind ),
			repr( self.created ) )


class Image:

	def __init__( self, data ):
		"""
		:param data: data dictionary. Usually FX API server response as JSON dictionary
		:raise fxservice.FXError: thrown if expected response fields are missing or another exception occurred

		Members: 

		- str kind: Type of asset
		- str region: The id of the region for this object
		- str project_id: The project ID this image belongs to.
		- str name: The name (or filename) of the asset
		- datetime created: Creation time of asset
		"""
		try:
			self.kind = 'Image' # Type of asset
			self.region = data["region"] # The id of the region for this object
			self.project_id = data["project_id"] # The project ID this image belongs to.
			self.name = data["name"] # The name (or filename) of the asset
			self.created = fxconverters.to_datetime( data["date_created"] ) # Creation time of asset
		except KeyError as detail:
			raise fxservice.FXResponseError( 'Image: missing field "%s" in server response %s' % (detail.args[0], repr( data )) )
		except (ValueError, TypeError) as detail:
			raise fxservice.FXResponseError( 'Image: "%s" for server response %s' % (detail.args[0], repr( data )) )
		except Exception as detail:
			raise fxservice.FXInternalError( 'Image: "%s" for server response %s' % (detail.args[0], repr( data )) )


	def __repr__( self ):
		return 'Image( {"kind": %s, "region": %s, "project_id": %s, "name": %s, "created": %s} )' % (
			repr( self.kind ),
			repr( self.region ),
			repr( self.project_id ),
			repr( self.name ),
			repr( self.created ) )


class Trackdata:

	def __init__( self, data ):
		"""
		:param data: data dictionary. Usually FX API server response as JSON dictionary
		:raise fxservice.FXError: thrown if expected response fields are missing or another exception occurred

		Members: 

		- str kind: Type of asset
		- str region: The id of the region for this object
		- str project_id: The project ID this trackdata object belongs to.
		- str name: The name (or filename) of the asset
		- datetime created: 
		"""
		try:
			self.kind = 'Trackdata' # Type of asset
			self.region = data["region"] # The id of the region for this object
			self.project_id = data["project_id"] # The project ID this trackdata object belongs to.
			self.name = data["name"] # The name (or filename) of the asset
			self.created = fxconverters.to_datetime( data["date_created"] )
		except KeyError as detail:
			raise fxservice.FXResponseError( 'Trackdata: missing field "%s" in server response %s' % (detail.args[0], repr( data )) )
		except (ValueError, TypeError) as detail:
			raise fxservice.FXResponseError( 'Trackdata: "%s" for server response %s' % (detail.args[0], repr( data )) )
		except Exception as detail:
			raise fxservice.FXInternalError( 'Trackdata: "%s" for server response %s' % (detail.args[0], repr( data )) )


	def __repr__( self ):
		return 'Trackdata( {"kind": %s, "region": %s, "project_id": %s, "name": %s, "created": %s} )' % (
			repr( self.kind ),
			repr( self.region ),
			repr( self.project_id ),
			repr( self.name ),
			repr( self.created ) )


class AuxData:

	def __init__( self, data ):
		"""
		:param data: data dictionary. Usually FX API server response as JSON dictionary
		:raise fxservice.FXError: thrown if expected response fields are missing or another exception occurred

		Members: 

		- str kind: Type of asset
		- str region: The id of the region for this object
		- str project_id: The project ID this data asset belongs to.
		- str name: The name (or filename) of the asset
		- datetime created: Creation time of asset
		- datetime modified: Modification time of asset
		"""
		try:
			self.kind = 'AuxData' # Type of asset
			self.region = data["region"] # The id of the region for this object
			self.project_id = data["project_id"] # The project ID this data asset belongs to.
			self.name = data["name"] # The name (or filename) of the asset
			self.created = fxconverters.to_datetime( data["date_created"] ) # Creation time of asset
			self.modified = fxconverters.to_datetime( data["date_modified"] ) # Modification time of asset
		except KeyError as detail:
			raise fxservice.FXResponseError( 'AuxData: missing field "%s" in server response %s' % (detail.args[0], repr( data )) )
		except (ValueError, TypeError) as detail:
			raise fxservice.FXResponseError( 'AuxData: "%s" for server response %s' % (detail.args[0], repr( data )) )
		except Exception as detail:
			raise fxservice.FXInternalError( 'AuxData: "%s" for server response %s' % (detail.args[0], repr( data )) )


	def __repr__( self ):
		return 'AuxData( {"kind": %s, "region": %s, "project_id": %s, "name": %s, "created": %s, "modified": %s} )' % (
			repr( self.kind ),
			repr( self.region ),
			repr( self.project_id ),
			repr( self.name ),
			repr( self.created ),
			repr( self.modified ) )


class Font:

	def __init__( self, data ):
		"""
		:param data: data dictionary. Usually FX API server response as JSON dictionary
		:raise fxservice.FXError: thrown if expected response fields are missing or another exception occurred

		Members: 

		- str kind: Type of asset
		- str region: The id of the region for this object
		- str project_id: The project ID this font asset belongs to.
		- str name: The name (or filename) of the asset
		- datetime created: Creation time of asset
		- datetime modified: Modification time of asset
		"""
		try:
			self.kind = 'Font' # Type of asset
			self.region = data["region"] # The id of the region for this object
			self.project_id = data["project_id"] # The project ID this font asset belongs to.
			self.name = data["name"] # The name (or filename) of the asset
			self.created = fxconverters.to_datetime( data["date_created"] ) # Creation time of asset
			self.modified = fxconverters.to_datetime( data["date_modified"] ) # Modification time of asset
		except KeyError as detail:
			raise fxservice.FXResponseError( 'Font: missing field "%s" in server response %s' % (detail.args[0], repr( data )) )
		except (ValueError, TypeError) as detail:
			raise fxservice.FXResponseError( 'Font: "%s" for server response %s' % (detail.args[0], repr( data )) )
		except Exception as detail:
			raise fxservice.FXInternalError( 'Font: "%s" for server response %s' % (detail.args[0], repr( data )) )


	def __repr__( self ):
		return 'Font( {"kind": %s, "region": %s, "project_id": %s, "name": %s, "created": %s, "modified": %s} )' % (
			repr( self.kind ),
			repr( self.region ),
			repr( self.project_id ),
			repr( self.name ),
			repr( self.created ),
			repr( self.modified ) )


class Sound:

	def __init__( self, data ):
		"""
		:param data: data dictionary. Usually FX API server response as JSON dictionary
		:raise fxservice.FXError: thrown if expected response fields are missing or another exception occurred

		Members: 

		- str kind: Type of asset
		- str region: The id of the region for this object
		- str project_id: The project ID this video asset belongs to.
		- str name: The name (or filename) of the asset
		- str uid: The UID of this video asset
		- datetime created: Creation time of asset
		- datetime modified: Modification time of asset
		- str acodec: The audio codec (currently 'acodec')
		- int channels: The number of audio channels
		- int framesize: The audio framesize
		- int numsamples: The number of samples (per channel?)
		- int samplefmt: The number of bits per sample (currently 0)
		- int samplerate: The samplerate in Hz
		"""
		try:
			self.kind = 'Sound' # Type of asset
			self.region = data["region"] # The id of the region for this object
			self.project_id = data["project_id"] # The project ID this video asset belongs to.
			self.name = data["name"] # The name (or filename) of the asset
			self.uid = data["uid"] # The UID of this video asset
			self.created = fxconverters.to_datetime( data["date_created"] ) # Creation time of asset
			self.modified = fxconverters.to_datetime( data["date_modified"] ) # Modification time of asset
			self.acodec = data["acodec"] # The audio codec (currently 'acodec')
			self.channels = data["channels"] # The number of audio channels
			self.framesize = data["framesize"] # The audio framesize
			self.numsamples = data["numsamples"] # The number of samples (per channel?)
			self.samplefmt = data["numsamples"] # The number of bits per sample (currently 0)
			self.samplerate = data["samplerate"] # The samplerate in Hz
		except KeyError as detail:
			raise fxservice.FXResponseError( 'Sound: missing field "%s" in server response %s' % (detail.args[0], repr( data )) )
		except (ValueError, TypeError) as detail:
			raise fxservice.FXResponseError( 'Sound: "%s" for server response %s' % (detail.args[0], repr( data )) )
		except Exception as detail:
			raise fxservice.FXInternalError( 'Sound: "%s" for server response %s' % (detail.args[0], repr( data )) )


	def __repr__( self ):
		return 'Sound( {"kind": %s, "region": %s, "project_id": %s, "name": %s, "uid": %s, "created": %s, "modified": %s, "acodec": %s, "channels": %s, "framesize": %s, "numsamples": %s, "samplefmt": %s, "samplerate": %s} )' % (
			repr( self.kind ),
			repr( self.region ),
			repr( self.project_id ),
			repr( self.name ),
			repr( self.uid ),
			repr( self.created ),
			repr( self.modified ),
			repr( self.acodec ),
			repr( self.channels ),
			repr( self.framesize ),
			repr( self.numsamples ),
			repr( self.samplefmt ),
			repr( self.samplerate ) )


class Video:

	def __init__( self, data ):
		"""
		:param data: data dictionary. Usually FX API server response as JSON dictionary
		:raise fxservice.FXError: thrown if expected response fields are missing or another exception occurred

		Members: 

		- str kind: Type of asset
		- str region: The id of the region for this object
		- str project_id: The project ID this video asset belongs to.
		- str name: The name (or filename) of the asset
		- str uid: The UID of this video asset
		- datetime created: Creation time of asset
		- datetime modified: Modification time of asset
		- Fraction fps: FPS as Fraction
		- Fraction avg_fps: Average FPS as Fraction
		- Fraction par: PAR as Fraction
		- Fraction dar: DAR as Fraction
		- Fraction tbn: TBN as Fraction
		- Fraction tbc: TBC as Fraction
		- str acodec: The audio codec (currently 'acodec')
		- int channels: The number of audio channels
		- int framesize: The audio framesize
		- int numsamples: The number of samples (per channel?)
		- int samplefmt: The number of bits per sample (currently 0)
		- int samplerate: The samplerate in Hz
		"""
		try:
			self.kind = 'Video' # Type of asset
			self.region = data["region"] # The id of the region for this object
			self.project_id = data["project_id"] # The project ID this video asset belongs to.
			self.name = data["name"] # The name (or filename) of the asset
			self.uid = data["uid"] # The UID of this video asset
			self.created = fxconverters.to_datetime( data["date_created"] ) # Creation time of asset
			self.modified = fxconverters.to_datetime( data["date_modified"] ) # Modification time of asset
			self.fps = fxconverters.to_fraction( data["fps"] ) # FPS as Fraction
			self.avg_fps = fxconverters.to_fraction( data["avg_fps"] ) # Average FPS as Fraction
			self.par = fxconverters.to_fraction( data["par"] ) # PAR as Fraction
			self.dar = fxconverters.to_fraction( data["dar"] ) # DAR as Fraction
			self.tbn = fxconverters.to_fraction( data["tbn"] ) # TBN as Fraction
			self.tbc = fxconverters.to_fraction( data["tbc"] ) # TBC as Fraction
			self.acodec = data["acodec"] # The audio codec (currently 'acodec')
			self.channels = data["channels"] # The number of audio channels
			self.framesize = data["framesize"] # The audio framesize
			self.numsamples = data["numsamples"] # The number of samples (per channel?)
			self.samplefmt = data["numsamples"] # The number of bits per sample (currently 0)
			self.samplerate = data["samplerate"] # The samplerate in Hz
		except KeyError as detail:
			raise fxservice.FXResponseError( 'Video: missing field "%s" in server response %s' % (detail.args[0], repr( data )) )
		except (ValueError, TypeError) as detail:
			raise fxservice.FXResponseError( 'Video: "%s" for server response %s' % (detail.args[0], repr( data )) )
		except Exception as detail:
			raise fxservice.FXInternalError( 'Video: "%s" for server response %s' % (detail.args[0], repr( data )) )


	def __repr__( self ):
		return 'Video( {"kind": %s, "region": %s, "project_id": %s, "name": %s, "uid": %s, "created": %s, "modified": %s, "fps": %s, "avg_fps": %s, "par": %s, "dar": %s, "tbn": %s, "tbc": %s, "acodec": %s, "channels": %s, "framesize": %s, "numsamples": %s, "samplefmt": %s, "samplerate": %s} )' % (
			repr( self.kind ),
			repr( self.region ),
			repr( self.project_id ),
			repr( self.name ),
			repr( self.uid ),
			repr( self.created ),
			repr( self.modified ),
			repr( self.fps ),
			repr( self.avg_fps ),
			repr( self.par ),
			repr( self.dar ),
			repr( self.tbn ),
			repr( self.tbc ),
			repr( self.acodec ),
			repr( self.channels ),
			repr( self.framesize ),
			repr( self.numsamples ),
			repr( self.samplefmt ),
			repr( self.samplerate ) )


class Datasource:

	def __init__( self, data ):
		"""
		:param data: data dictionary. Usually FX API server response as JSON dictionary
		:raise fxservice.FXError: thrown if expected response fields are missing or another exception occurred

		Members: 

		- str kind: Type of asset
		- str region: The id of the region for this object
		- str project_id: The project ID this datasource belongs to.
		- str name: The name (or filename) of the asset
		- datetime created: Creation time of asset
		- datetime modified: Modification time of asset
		"""
		try:
			self.kind = 'Datasource' # Type of asset
			self.region = data["region"] # The id of the region for this object
			self.project_id = data["project_id"] # The project ID this datasource belongs to.
			self.name = data["name"] # The name (or filename) of the asset
			self.created = fxconverters.to_datetime( data["date_created"] ) # Creation time of asset
			self.modified = fxconverters.to_datetime( data["date_modified"] ) # Modification time of asset
		except KeyError as detail:
			raise fxservice.FXResponseError( 'Datasource: missing field "%s" in server response %s' % (detail.args[0], repr( data )) )
		except (ValueError, TypeError) as detail:
			raise fxservice.FXResponseError( 'Datasource: "%s" for server response %s' % (detail.args[0], repr( data )) )
		except Exception as detail:
			raise fxservice.FXInternalError( 'Datasource: "%s" for server response %s' % (detail.args[0], repr( data )) )


	def __repr__( self ):
		return 'Datasource( {"kind": %s, "region": %s, "project_id": %s, "name": %s, "created": %s, "modified": %s} )' % (
			repr( self.kind ),
			repr( self.region ),
			repr( self.project_id ),
			repr( self.name ),
			repr( self.created ),
			repr( self.modified ) )


class StatusMessage:

	def __init__( self, data ):
		"""
		:param data: data dictionary. Usually FX API server response as JSON dictionary
		:raise fxservice.FXError: thrown if expected response fields are missing or another exception occurred

		Members: 

		"""
		pass
