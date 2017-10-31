from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.db.models import Q
from ohm2_handlers_light import utils as h_utils
from ohm2_handlers_light.definitions import RunException
from . import models as ohm2_addresses_light_models
from . import errors as ohm2_addresses_light_errors
from . import settings
import os, time, random


random_string = "ssWpCTQV9bSvXtI88PemcolGC9lmihmz"



def create_address(country, street = "", number = "", **kwargs):
	kwargs["country"] = country
	kwargs["street"] = street.strip()
	kwargs["number"] = number.strip()
	
	for level, value in parse_address_levels(kwargs).items():
		kwargs[level] = value

	coordinates = kwargs.get("coordinates", None)
	if coordinates:
		kwargs["coordinates"] = coordinates

	return h_utils.db_create(ohm2_addresses_light_models.Address, **kwargs)

def parse_address_levels(data):
	levels = (
		"first_level",
		"second_level",
		"third_level",
		"fourth_level",
	)
	parsed = {}
	for e in levels:
		level = data.get(e, None)
		if level:
			parsed[e] = level.strip().title()
	return parsed

def get_address(**kwargs):
	return h_utils.db_get(ohm2_addresses_light_models.Address, **kwargs)

def get_or_none_address(**kwargs):
	return h_utils.db_get_or_none(ohm2_addresses_light_models.Address, **kwargs)

def filter_address(**kwargs):
	return h_utils.db_filter(ohm2_addresses_light_models.Address, **kwargs)		

