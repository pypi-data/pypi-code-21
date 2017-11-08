from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password, password_changed, password_validators_help_texts
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.utils import timezone
from rest_framework.authtoken.models import Token
from ohm2_handlers_light import utils as h_utils
from ohm2_accounts_light import settings
from ohm2_accounts_light import models as ohm2_accounts_light_models
from ohm2_accounts_light import errors as ohm2_accounts_light_errors
from ohm2_handlers_light.definitions import RunException
from random import choice as random_choice
import importlib


def create_user(username, email, password, **kwargs):

	if settings.CHECK_PASSWORD_SECURE and not is_password_secure(password):
		raise RunException(**ohm2_accounts_light_errors.THE_PASSWORD_IS_NOT_SECURE)

	
	user = User.objects.create_user(username = username,
								    email = email,
								    password = password)
	

	return user

def get_user(**kwargs):
	return h_utils.db_get(User, **kwargs)

def get_or_none_user(**kwargs):
	return h_utils.db_get_or_none(User, **kwargs)

def filter_user(**kwargs):
	return h_utils.db_filter(obj = User, **kwargs)

def delete_user(user):
	return h_utils.db_delete(user)	

def get_or_create_authtoken(user):
	token, created = Token.objects.get_or_create(user = user)
	return token

def get_authtoken(user):
	return Token.objects.get(user = user)

def user_exist(**kwargs):
	if filter_user(**kwargs).count() > 0:
		return True
	return False

def change_password(user, password):
	user.set_password(password)
	user.save()
	return user

def user_authenticate(username, password):
	return authenticate(username = username, password = password)

def user_login(request, auth_user):
	return login(request, auth_user)

def user_logout(request):
	return logout(request)

def validate_current_password(password, user = None, password_validators = None):
	try:
		validate_password(password, user, password_validators)
	except ValidationError as e:
		return [reason for reason in e]
	return []

def is_password_secure(password, user = None, password_validators = None):
	errors = validate_current_password(password, user, password_validators)
	if len(errors) == 0:
		return True
	return False

def run_signup_pipeline(request, user, **kwargs):
	previous_outputs = {}
	for pipeline in settings.SIGNUP_PIPELINE:

		func = pipeline.rsplit(".", 1)[-1]
		
		m = importlib.import_module(pipeline)
		function = getattr(m, func)

		user, output = function(request, user, previous_outputs, **kwargs)

		previous_outputs = h_utils.join_dicts(previous_outputs, output)

	return None


def run_login_pipeline(request, auth_user, **kwargs):
	previous_outputs = {}
	for pipeline in settings.LOGIN_PIPELINE:

		func = pipeline.rsplit(".", 1)[-1]
		
		m = importlib.import_module(pipeline)
		function = getattr(m, func)

		auth_user, output = function(request, auth_user, previous_outputs)

		previous_outputs = h_utils.join_dicts(previous_outputs, output)

	return None

def run_logout_pipeline(request, **kwargs):
	previous_outputs = {}
	for pipeline in settings.LOGOUT_PIPELINE:

		func = pipeline.rsplit(".", 1)[-1]
		
		m = importlib.import_module(pipeline)
		function = getattr(m, func)

		output = function(request, previous_outputs)

		previous_outputs = h_utils.join_dicts(previous_outputs, output)

	return None

def create_passwordreset(user, **kwargs):
	kwargs["identity"] = h_utils.db_unique_random(ohm2_accounts_light_models.PasswordReset, 32)
	kwargs["user"] = user
	kwargs["code"] = get_passwordreset_code(5)
	return h_utils.db_create(ohm2_accounts_light_models.PasswordReset, **kwargs)

def get_passwordreset_code(length, **kwargs):
	possible_characters = "abcdefghkmnprstuvxyz123456789"
	
	max_tries, tries = 10, 0
	while tries < max_tries:
		tries += 1
		code = "".join(random_choice(possible_characters) for x in range(length))
		if get_or_none_passwordreset(code = code) is None:
			return code

	else:
		raise RunException(**ohm2_accounts_light_errors.NO_PASSWORD_RESET_FOUND)	


def get_passwordreset(**kwargs):
	return h_utils.db_get(ohm2_accounts_light_models.PasswordReset, **kwargs)

def get_or_none_passwordreset(**kwargs):
	return h_utils.db_get_or_none(ohm2_accounts_light_models.PasswordReset, **kwargs)

def send_passwordreset(passwordreset, request, **kwargs):
	context = {
		"ret" : {
			"passwordreset" : passwordreset,
			"website_url" : settings.WEBSITE_URL,
		},
	}

	content = h_utils.template_response(settings.PASSWORD_RESET_TEMPLATE_PATH, context)
	

	sent = h_utils.mailgun_send(passwordreset.user.email, settings.PASSWORD_RESET_FROM_EMAIL, _(settings.PASSWORD_RESET_SUBJECT), content)


	if sent:
		passwordreset = h_utils.db_update(passwordreset, last_sent_date = timezone.now())
	
	return (passwordreset, sent)


def change_password_with_passwordreset(passwordreset, password, **kwargs):
	user = change_password(passwordreset.user, password)
	return h_utils.db_update(passwordreset, activation_date = timezone.now())






