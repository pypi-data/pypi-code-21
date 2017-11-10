from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.db.models import Q
from ohm2_handlers_light import utils as h_utils
from ohm2_handlers_light.definitions import RunException
from . import models as onesignal_models
from . import errors as onesignal_errors
from . import settings
import os, time, random


random_string = "L4grZ9Lzlr7eByGMzCsullCuUkk2b8BO"


def create_device(user, platform, player_id, push_token, **kwargs):
	kwargs["gateway"] = onesignal_models.Device.gateway_onesignal[0]
	kwargs["user"] = user
	kwargs["platform"] = platform
	kwargs["player_id"] = player_id.strip()
	kwargs["push_token"] = push_token.strip()
	return h_utils.db_create(onesignal_models.Device, **kwargs)

def get_device(**kwargs):
	return h_utils.db_get(onesignal_models.Device, **kwargs)

def get_or_none_device(**kwargs):
	return h_utils.db_get_or_none(onesignal_models.Device, **kwargs)

def filter_device(**kwargs):
	return h_utils.db_filter(onesignal_models.Device, **kwargs)

def q_device(q):
	return h_utils.db_q(onesignal_models.Device, q)	

def update_device(device, **kwargs):
	return h_utils.db_update(device, **kwargs)	

def get_platform_ios():
	return onesignal_models.Device.platform_ios

def get_platform_android():
	return onesignal_models.Device.platform_android

def send_notifications(message, player_ids, **options):
	contents = {
		"en": message.title,
	}
	payload = {
		"app_id": settings.APP_ID,
		"include_player_ids": player_ids,
		"contents": contents,
		"data": message.get_onesignal_data(),
	}
	res = requests.post(settings.API_NOTIFICATIONS_URL, headers = settings.HEADERS, data = json.dumps(payload))
	if res.status_code != 200:
		raise RunException(**onesignal_errors.INVALID_NOTIFICATION_STATUS_CODE)
	ret = res.json()

	pushed = True
	return pushed


"""
def create_model(**kwargs):
	return h_utils.db_create(onesignal_models.Model, **kwargs)

def get_model(**kwargs):
	return h_utils.db_get(onesignal_models.Model, **kwargs)

def get_or_none_model(**kwargs):
	return h_utils.db_get_or_none(onesignal_models.Model, **kwargs)

def filter_model(**kwargs):
	return h_utils.db_filter(onesignal_models.Model, **kwargs)

def q_model(q):
	return h_utils.db_q(onesignal_models.Model, q)			
"""
