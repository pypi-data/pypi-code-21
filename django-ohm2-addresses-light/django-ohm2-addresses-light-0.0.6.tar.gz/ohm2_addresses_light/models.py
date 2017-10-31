from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.utils.translation import ugettext as _
from ohm2_handlers_light.models import GeoBaseModel
from ohm2_countries_light.models import Country
from . import managers
from . import settings




class Address(GeoBaseModel):
	country = models.ForeignKey(Country, on_delete = models.CASCADE)

	first_level = models.CharField(max_length = settings.STRING_NORMAL, null = True, blank = True, default = "")
	second_level = models.CharField(max_length = settings.STRING_NORMAL, null = True, blank = True, default = "")
	third_level = models.CharField(max_length = settings.STRING_NORMAL, null = True, blank = True, default = "")
	fourth_level = models.CharField(max_length = settings.STRING_NORMAL, null = True, blank = True, default = "")

	street = models.CharField(max_length = settings.STRING_NORMAL, null = True, blank = True, default = "")
	number = models.CharField(max_length = settings.STRING_NORMAL, null = True, blank = True, default = "")

	floor = models.CharField(max_length = settings.STRING_NORMAL, null = True, blank = True, default = "")
	tower = models.CharField(max_length = settings.STRING_NORMAL, null = True, blank = True, default = "")
	block = models.CharField(max_length = settings.STRING_NORMAL, null = True, blank = True, default = "")

	coordinates = models.PointField(srid = settings.SRID, null = True, blank = True, default = None)

	def __str__(self):
		formated = ""

		if self.first_level:
			formated += self.first_level

		if self.second_level:
			formated += (", " if len(formated) > 0 else "") + self.second_level

		if self.third_level:
			formated += (", " if len(formated) > 0 else "") + self.third_level

		if self.fourth_level:
			formated += (", " if len(formated) > 0 else "") + self.fourth_level

		if self.street:
			formated += (", " if len(formated) > 0 else "") + self.street

		if self.number:
			formated += (", " if len(formated) > 0 else "") + self.number

		formated += (", " if len(formated) > 0 else "") + self.country.name

		if self.coordinates:
			formated += (", " if len(formated) > 0 else "") + "{0}".format(self.coordinates.coords)

		return formated


	@property
	def by_lines(self):
	    return self.__str__().split(",")	