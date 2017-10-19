from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.db.models import Q
from ohm2_handlers_light import utils as h_utils
from ohm2_handlers_light.definitions import RunException
from . import models as ohm2_countries_light_models
from . import errors as ohm2_countries_light_errors
from . import settings
import os, time, random


random_string = "Re4Wwe69YRenGntPO8ADErMBs1Y4hCLQ"

	

def create_country(name, official_name, alpha_2, alpha_3, numeric, **kwargs):
	kwargs["name"] = name.strip().title()
	kwargs["official_name"] = official_name.strip().title()
	kwargs["alpha_2"] = alpha_2.strip()
	kwargs["alpha_3"] = alpha_3.strip()
	kwargs["numeric"] = numeric

	flag_small = kwargs.get("flag_small")
	if flag_small:
		kwargs["flag_small"] = process_country_flag_small_image(flag_small)
		
	return h_utils.db_create(ohm2_countries_light_models.Country, **kwargs)

def process_country_flag_small_image(image, **kwargs):
	extension = h_utils.get_file_extension(image.name)
	if extension is None:
		return image
	else:
		extension = extension.lower()

	
	save_options = {
		"max_width": 48,
		"max_height": 48,
	}
		
	if extension in ["jpg", "jpeg"]:
		save_options["format"] = "JPEG"
		save_options["quality"] = 95
		save_options["optimize"] = True

	elif extension == "png":
		save_options["format"] = "PNG"
		save_options["quality"] = 95
		save_options["optimize"] = True
	
	else:
		pass


	options = {
		"save_options": save_options,
	}
	return h_utils.process_uploaded_image_2(image, **options)

def get_country(**kwargs):
	return h_utils.db_get(ohm2_countries_light_models.Country, **kwargs)

def get_or_none_country(**kwargs):
	return h_utils.db_get_or_none(ohm2_countries_light_models.Country, **kwargs)

def filter_country(**kwargs):
	return h_utils.db_filter(ohm2_countries_light_models.Country, **kwargs)		

def update_country(country, **kwargs):
	params = {}

	flag_small = kwargs.get("flag_small")
	if flag_small:
		params["flag_small"] = process_country_flag_small_image(flag_small)	

	return h_utils.db_update(country, **params)

