from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from ohm2_handlers_light import managers as ohm2_handlers_light_managers
from ohm2_handlers_light import settings


class BaseModel(models.Model):
	identity = models.CharField(max_length=settings.STRING_DOUBLE, unique = True)
	created = models.DateTimeField(default = timezone.now)
	last_update = models.DateTimeField(default = timezone.now)
	
	objects = ohm2_handlers_light_managers.OHM2HandlersLightManager()

	def __str__(self):
		return self.identity

	class Meta:
		abstract = True


class BaseError(BaseModel):
	app = models.CharField(max_length=settings.STRING_DOUBLE)
	code = models.IntegerField(default = -1)
	message = models.TextField(default = "")
	extra = models.TextField(default = "")
	
	ins_filename = models.CharField(max_length=settings.STRING_DOUBLE, null = True, blank = True, default = "")
	ins_lineno = models.IntegerField(null = True, blank = True, default = 0)
	ins_function = models.CharField(max_length=settings.STRING_DOUBLE, null = True, blank = True, default = "")
	ins_code_context = models.TextField(null = True, blank = True, default = "")

	def __str__(self):
		return "{0}|{1}|{2}|{3}".format(self.identity, self.app, self.code, self.message)



if settings.INCLUDE_GEOBASEMODEL:
	from django.contrib.gis.db import models as geomodels

	class GeoBaseModel(geomodels.Model):
		identity = geomodels.CharField(max_length=settings.STRING_DOUBLE, unique = True)
		created = geomodels.DateTimeField(default = timezone.now)
		last_update = geomodels.DateTimeField(default = timezone.now)
		
		objects = ohm2_handlers_light_managers.OHM2HandlersLightGeoManager()

		def __str__(self):
			return self.identity

		class Meta:
			abstract = True


			