from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from ohm2_handlers_light import utils as h_utils
from ohm2_handlers_light.parsers import get_as_or_get_default
from ohm2_pushes_light import models as ohm2_pushes_light_models
from . import dispatcher
from . import settings



def process_gateways_onesignal_register_device(request, platform):
	keys = (
		("player_id", "player_id", ""),
		("push_token", "push_token", ""),
		("platform", h_utils.random_string(10), platform),
	)
	res, error = dispatcher.gateways_onesignal_register_device(request, get_as_or_get_default(request.data, keys))
	if error:
		return JsonResponse({"error": error.regroup()})
	return JsonResponse(res)


@api_view(['POST'])
@authentication_classes((TokenAuthentication, SessionAuthentication))
@permission_classes((IsAuthenticated,))
def gateways_onesignal_register_device_android(request):
	"""
	Register Device (Android)

	
	__Inputs__:

		- player_id (string, required): device's player id
		- push_token (string, required): device's push token

	__Output__:

		- error (json-dict): describes the error (if known) with a code (integer) and a message (string).
		- ret (boolean): true if the signup completed succesfully.

	__Notes__:

		- 
	
	"""
	return process_gateways_onesignal_register_device(request, ohm2_pushes_light_models.Device.platform_android[0])
	

@api_view(['POST'])
@authentication_classes((TokenAuthentication, SessionAuthentication))
@permission_classes((IsAuthenticated,))
def gateways_onesignal_register_device_ios(request):
	"""
	Register Device (iOS)

	
	__Inputs__:

		- player_id (string, required): device's player id
		- push_token (string, required): device's push token

	__Output__:

		- error (json-dict): describes the error (if known) with a code (integer) and a message (string).
		- ret (boolean): true if the signup completed succesfully.

	__Notes__:

		- 
	
	"""
	return process_gateways_onesignal_register_device(request, ohm2_pushes_light_models.Device.platform_ios[0])


	
	



