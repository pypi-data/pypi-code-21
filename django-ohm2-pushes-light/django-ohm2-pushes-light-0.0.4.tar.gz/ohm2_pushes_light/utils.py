from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.db.models import Q
from ohm2_handlers_light import utils as h_utils
from ohm2_handlers_light.definitions import RunException
from ohm2_pushes_light.gateways.onesignal import utils as onesignal_utils
from ohm2_pushes_light.gateways.firebase import utils as firebase_utils
from . import models as ohm2_pushes_light_models
from . import errors as ohm2_pushes_light_errors
from . import settings
from . import definitions as ohm2_pushes_light_definitions
import os, time, random


random_string = "RL6G7j5snwNojousZp25qqKZu38NMi3w"


def create_message(user, title, body, **kwargs):
	kwargs["user"] = user
	kwargs["title"] = title.strip()
	kwargs["body"] = body.strip()
	return h_utils.db_create(ohm2_pushes_light_models.Message, **kwargs)

def get_message(**kwargs):
	return h_utils.db_get(ohm2_pushes_light_models.Message, **kwargs)

def get_or_none_message(**kwargs):
	return h_utils.db_get_or_none(ohm2_pushes_light_models.Message, **kwargs)

def filter_message(**kwargs):
	return h_utils.db_filter(ohm2_pushes_light_models.Message, **kwargs)

def q_message(q):
	return h_utils.db_q(ohm2_pushes_light_models.Message, q)

def create_dummy_message(user, title, body, **kwargs):
	message = ohm2_pushes_light_definitions.DummyMessage(user, title, body, **kwargs)
	return message

def get_user_devices(user, **options):
	providers = (
		{
			"gateway": settings.GATEWAY_ONESIGNAL[0],
			"getter": onesignal_utils.filter_device,
		},
	)
	querysets = {}
	for p in providers:
		querysets[p["gateway"]] = p["getter"](user = user).order_by("-last_update")
	return querysets


def send_notification(message, **options):
	summary = {}
	for gateway, queryset in get_user_devices(message.user).items():

		if gateway == settings.GATEWAY_ONESIGNAL[0]:
			player_ids = [device.player_id for device in queryset]
			summary[gateway] = onesignal_utils.send_notifications(message, player_ids, **options.get("onesignal_options", {}))

		elif gateway == settings.GATEWAY_FIREBASE[0]:
			pass

	return summary		

def mark_message_as_read(message, **options):
	return h_utils.db_update(message, read = True)

"""
def create_model(**kwargs):
	return h_utils.db_create(ohm2_pushes_light_models.Model, **kwargs)

def get_model(**kwargs):
	return h_utils.db_get(ohm2_pushes_light_models.Model, **kwargs)

def get_or_none_model(**kwargs):
	return h_utils.db_get_or_none(ohm2_pushes_light_models.Model, **kwargs)

def filter_model(**kwargs):
	return h_utils.db_filter(ohm2_pushes_light_models.Model, **kwargs)

def q_model(q):
	return h_utils.db_q(ohm2_pushes_light_models.Model, q)			
"""
