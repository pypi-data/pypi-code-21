from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.db.models import Q
from ohm2_handlers_light import utils as h_utils
from ohm2_handlers_light.definitions import RunException
from . import models as firebase_models
from . import errors as firebase_errors
from . import settings
import os, time, random


random_string = "v91XnXLG4n4eYSugPuwd7xYTVknj43rH"



"""
def create_model(**kwargs):
	return h_utils.db_create(firebase_models.Model, **kwargs)

def get_model(**kwargs):
	return h_utils.db_get(firebase_models.Model, **kwargs)

def get_or_none_model(**kwargs):
	return h_utils.db_get_or_none(firebase_models.Model, **kwargs)

def filter_model(**kwargs):
	return h_utils.db_filter(firebase_models.Model, **kwargs)

def q_model(q):
	return h_utils.db_q(firebase_models.Model, q)			
"""
