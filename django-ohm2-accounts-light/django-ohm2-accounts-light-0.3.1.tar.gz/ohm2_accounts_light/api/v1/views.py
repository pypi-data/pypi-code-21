from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from ohm2_handlers_light.parsers import get_as_or_get_default
from . import dispatcher
from . import settings



@api_view(['POST'])
@permission_classes((AllowAny,))
def signup(request):
	"""
	User signup (without authentication token)

	
	__Inputs__:

		- username (string, required): user's username
		- password (string, required): user's password
		- email (string-email, optional): user's email
		- user_info (json-obj, optional):
			&#09;- first_name
			&#09;- last_name

	__Output__:

		- error (json-dict): describes the error (if known) with a code (integer) and a message (string).
		- ret (boolean): true if the signup completed succesfully.

	__Notes__:

		- If username is an email, the email parameter will be overriten by username.	
	
	"""

	keys = (
		("username", "username", ""),
		("password", "password", ""),
		("email", "email", ""),
		("user_information", "user_info", {}),
	)
	res, error = dispatcher.signup(request, get_as_or_get_default(request.data, keys))
	if error:
		return JsonResponse({"error": error.regroup()})
	return JsonResponse(res)


@api_view(['POST'])
@permission_classes((AllowAny,))
def login(request):
	"""
	User login (without authentication token)
	

	__Inputs__:

		- username (string, required): user's username
		- password (string, required): user's password

	__Output__:

		- error (json-dict): describes the error (if known) with a code (integer) and a message (string).
		- ret (boolean): true if the login completed succesfully.

	__Notes__:

		- None

	"""
	keys = (
		("username", "username", ""),
		("password", "password", ""),
	)
	res, error = dispatcher.login(request, get_as_or_get_default(request.data, keys))
	if error:
		return JsonResponse({"error": error.regroup()})
	return JsonResponse(res)


@api_view(['POST'])
@authentication_classes((TokenAuthentication, SessionAuthentication))
@permission_classes((IsAuthenticated,))
def logout(request):
	"""
	User logout


	__Inputs__:

		- None

	__Output__:

		- error (json-dict): describes the error (if known) with a code (integer) and a message (string).
		- ret (boolean): true if the logout completed succesfully.

	__Notes__:

		- None

	"""
	keys = (
	)
	res, error = dispatcher.logout(request, get_as_or_get_default(request.data, keys))
	if error:
		return JsonResponse({"error": error.regroup()})
	return JsonResponse(res)




def process_signup_and_get_token(request):
	keys = (
		("username", "username", ""),
		("password", "password", ""),
		("email", "email", ""),
		("user_information", "user_info", {}),
	)
	res, error = dispatcher.signup_and_get_token(request, get_as_or_get_default(request.data, keys))
	if error:
		return JsonResponse({"error": error.regroup()})
	return JsonResponse(res)


@api_view(['POST'])
@permission_classes((AllowAny,))
def signup_and_get_token(request):
	"""
	User signup (with authentication token)


	__Inputs__:
		- username (string, required): user's username
		- password (string, required): user's password
		- email (string-email, optional): user's email

	__Output__:
		- error (json-dict): describes the error (if known) with a code (integer) and a message (string).
		- ret (json-dict): 
			&#09;- token (string): user's authentication token

	__Notes__:
		- If username is an email, the email parameter will be overriten by username.

	"""
	return process_signup_and_get_token(request)


@api_view(['POST'])
@csrf_exempt
def signup_and_get_token_patched(request):
	return process_signup_and_get_token(request)






def process_login_and_get_token(request):
	keys = (
		("username", "username", ""),
		("password", "password", ""),
	)
	res, error = dispatcher.login_and_get_token(request, get_as_or_get_default(request.data, keys))
	if error:
		return JsonResponse({"error": error.regroup()})
	return JsonResponse(res)

@api_view(['POST'])
@permission_classes((AllowAny,))
def login_and_get_token(request):
	"""
	User login (with authentication token)


	__Inputs__:

		- username (string, required): user's username
		- password (string, required): user's password

	__Output__:

		- error (json-dict): describes the error (if known) with a code (integer) and a message (string).
		- ret (json-dict): 
			&#09;- token (string): user's authentication token

	__Notes__:

		- None

	"""
	return process_login_and_get_token(request)


@api_view(['POST'])
@csrf_exempt
def login_and_get_token_patched(request):
	return process_login_and_get_token(request)


@api_view(['POST'])
@permission_classes((AllowAny,))
def send_password_reset_link(request):
	"""
	Send password reset


	__Inputs__:

		- username (string, required): user's username

	__Output__:

		- error (json-dict): describes the error (if known) with a code (integer) and a message (string).
		- ret (boolean): true if password link/code was sent succesfully

	__Notes__:

		- None

	"""
	keys = (
		("username", "username", ""),
	)
	res, error = dispatcher.send_password_reset_link(request, get_as_or_get_default(request.data, keys))
	if error:
		return JsonResponse({"error": error.regroup()})
	return JsonResponse(res)


@api_view(['POST'])
@permission_classes((AllowAny,))
def set_password_reset(request):
	"""
	Set password reset


	__Inputs__:

		- username (string, required): user's username
		- password (string, required): user's new password
		- identity (string, optional): password reset's identity (for web app)
		- code (string, optional): password reset's identity (for mobile apps)


	__Output__:

		- error (json-dict): describes the error (if known) with a code (integer) and a message (string).
		- ret (boolean): true if password link/code was sent succesfully

	__Notes__:

		- None

	"""
	keys = (
		("username", "username", ""),
		("password", "password", ""),
		("identity", "identity", ""),
		("code", "code", ""),
	)
	res, error = dispatcher.set_password_reset(request, get_as_or_get_default(request.data, keys))
	if error:
		return JsonResponse({"error": error.regroup()})
	return JsonResponse(res)


@api_view(['POST'])
@permission_classes((AllowAny,))
def set_password_reset_and_get_token(request):
	"""
	Set password reset (with authentication token)


	__Inputs__:

		- username (string, required): user's username
		- password (string, required): user's new password
		- identity (string, optional): password reset's identity (for web app)
		- code (string, optional): password reset's identity (for mobile apps)


	__Output__:

		- error (json-dict): describes the error (if known) with a code (integer) and a message (string).
		- ret (json-dict): 
			&#09;- token (string): user's authentication token

	__Notes__:

		- None

	"""
	keys = (
		("username", "username", ""),
		("password", "password", ""),
		("identity", "identity", ""),
		("code", "code", ""),
	)
	res, error = dispatcher.set_password_reset(request, get_as_or_get_default(request.data, keys))
	if error:
		return JsonResponse({"error" : error.regroup()})

	elif res.get("error") or not res.get("ret"):
		return JsonResponse({"error" : res.get("error", {"code": -1, "message" : "an error occured"})})

	else:
		res, error = dispatcher.get_authtoken(request, get_as_or_get_default(request.data, (("username", "username", ""),)))

	if error:
		return JsonResponse({"error": error.regroup()})
	return JsonResponse(res)


@api_view(['POST'])
@authentication_classes((TokenAuthentication, SessionAuthentication))
@permission_classes((IsAuthenticated,))
def update_user_information(request):
	"""
	Update user information


	__Inputs__:

		- firstname (string, optional): user's firstname
		- lastname (string, optional): user's lastname


	__Output__:

		- error (json-dict): describes the error (if known) with a code (integer) and a message (string).
		- ret (boolean): true if password link/code was sent succesfully

	__Notes__:

		- None

	"""
	keys = (
		("firstname", "firstname", ""),
		("lastname", "lastname", ""),
	)
	res, error = dispatcher.update_user_information(request, get_as_or_get_default(request.data, keys))
	if error:
		return JsonResponse({"error": error.regroup()})
	return JsonResponse(res)



def process_facebook_login_and_get_token(request):
	keys = (
		("access_token", "access_token", ""),
	)
	res, error = dispatcher.facebook_login_and_get_token(request, get_as_or_get_default(request.data, keys))
	if error:
		return JsonResponse({"error": error.regroup()})
	return JsonResponse(res)


@api_view(['POST'])
@permission_classes((AllowAny,))
def facebook_login_and_get_token(request):
	"""
	Facebook login and get auth token


	__Inputs__:

		- access_token (string, required): google plus token


	__Output__:

		- error (json-dict): describes the error (if known) with a code (integer) and a message (string).
		- ret (json-dict): 
			&#09;- token (string): user's authentication token
			&#09;- username (string): username assigned

	__Notes__:

		- None

	"""
	return process_facebook_login_and_get_token(request)
	

@api_view(['POST'])
@csrf_exempt
def facebook_login_and_get_token_patched(request):
	return process_facebook_login_and_get_token(request)



def process_google_plus_login_and_get_token(request):
	keys = (
		("access_token", "access_token", ""),
	)
	res, error = dispatcher.google_plus_login_and_get_token(request, get_as_or_get_default(request.data, keys))
	if error:
		return JsonResponse({"error": error.regroup()})
	return JsonResponse(res)


@api_view(['POST'])
@permission_classes((AllowAny,))
def google_plus_login_and_get_token(request):
	"""
	Google plus login and get auth token


	__Inputs__:

		- access_token (string, required): google plus token


	__Output__:

		- error (json-dict): describes the error (if known) with a code (integer) and a message (string).
		- ret (json-dict): 
			&#09;- token (string): user's authentication token
			&#09;- username (string): username assigned

	__Notes__:

		- None

	"""
	return process_google_plus_login_and_get_token(request)


@api_view(['POST'])
@csrf_exempt
def google_plus_login_and_get_token_patched(request):
	return process_google_plus_login_and_get_token(request)



