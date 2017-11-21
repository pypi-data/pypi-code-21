from django.db import models
from . import utils as h_utils
from . import settings


class OHM2HandlersLightManager(models.Manager):
	
	def create(self, *args, **kwargs):
		if kwargs.get("identity") is None:
			kwargs["identity"] = h_utils.db_unique_random(self.model)
		return super(OHM2HandlersLightManager, self).create(*args, **kwargs)
	
	def save(self, *args, **kwargs):
		return super(OHM2HandlersLightManager, self).save(*args, **kwargs)


if settings.INCLUDE_GEOBASEMODEL:

	from django.contrib.gis.db import models as geomodels
	class OHM2HandlersLightGeoManager(geomodels.Manager):
		
		def create(self, *args, **kwargs):
			if kwargs.get("identity") is None:
				kwargs["identity"] = h_utils.db_unique_random(self.model)
			return super(OHM2HandlersLightGeoManager, self).create(*args, **kwargs)
		
		def save(self, *args, **kwargs):
			return super(OHM2HandlersLightGeoManager, self).save(*args, **kwargs)