from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils import timezone
from django.utils.translation import ugettext as _
from ohm2_handlers_light.models import BaseModel
from . import managers
from . import settings



class Country(BaseModel):
	name = models.CharField(max_length = settings.STRING_NORMAL, validators = [MinLengthValidator(1)])
	official_name = models.CharField(max_length = settings.STRING_NORMAL, validators = [MinLengthValidator(1)])
	alpha_2 = models.CharField(max_length = settings.STRING_SHORT, validators = [MinLengthValidator(2)])
	alpha_3	= models.CharField(max_length = settings.STRING_SHORT, validators = [MinLengthValidator(3)])
	numeric = models.IntegerField()
	flag_small = models.ImageField(upload_to = managers.country_flag_small_upload_to)


	def __str__(self):
		return "%s [alpha 2: %s][alpha 3: %s]" % (self.name, self.alpha_2, self.alpha_3)
		
	@property
	def flag_small_url(self):
		if self.flag_small:
			return self.flag_small.url
		return None	