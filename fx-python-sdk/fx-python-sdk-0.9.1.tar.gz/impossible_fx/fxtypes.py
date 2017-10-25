"""
	Result base Class and additional result types for Impossible FX API
"""

class Assets:
	"""
	Bundle Assets
	"""

	def __init__( self, all, sounds, videos, images, fonts, datasources, aux, trackdata ):
		self.all = all
		self.sounds = sounds
		self.videos = videos
		self.images = images
		self.fonts = fonts
		self.datasources = datasources
		self.aux = aux
		self.trackdata = trackdata

