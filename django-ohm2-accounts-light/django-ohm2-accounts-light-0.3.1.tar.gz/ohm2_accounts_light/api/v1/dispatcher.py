from ohm2_handlers_light import utils as h_utils
from ohm2_accounts_light.decorators import ohm2_accounts_light_safe_request
from ohm2_accounts_light import utils as ohm2_accounts_light_utils
from ohm2_accounts_light import settings
from . import errors as api_v1_errors
from . import settings as api_v1_settings
import requests

if api_v1_settings.FACEBOOK_LOGIN:
	import facebook



@ohm2_accounts_light_safe_request
def signup(request, params, **pipeline_options):
	p = h_utils.cleaned(params, (
							("string", "username", 1),
							("string", "password", 1),
							("string", "email", 0),
							("def_dict", "user_information", (
								("first_name", ""),
								("last_name", ""),
							)),
						))

	if request.user.is_authenticated():
		return {"error": api_v1_errors.USER_ALREADY_LOGGED_IN}
	
	elif ohm2_accounts_light_utils.user_exist(username = p["username"]):
		return {"error" : api_v1_errors.USER_ALREADY_EXIST}

	elif settings.CHECK_PASSWORD_SECURE and not ohm2_accounts_light_utils.is_password_secure(p["password"]):
		return {"error" : api_v1_errors.THE_PASSWORD_IS_NOT_SECURE}

	elif len(p["email"]) > 0 and not h_utils.is_email_valid(p["email"]):
		return {"error" : api_v1_errors.INVALID_EMAIL}

	elif not settings.SIGNUPS_ENABLED:
		return {"error" : api_v1_errors.SIGNUPS_DISABLED}

	else:
		pass


	username, password, email = p["username"], p["password"], p["email"]
	if len(email) == 0 and h_utils.is_email_valid(username):
		email = username

	

	pipeline_options["username"] = username
	pipeline_options["email"] = email
	pipeline_options["password"] = password

	
	pipeline_options["ohm2_user_information"] = p["user_information"]


	user = ohm2_accounts_light_utils.create_user(username, email, password)
	try:
		ohm2_accounts_light_utils.run_signup_pipeline(request, user, **pipeline_options)
	except Exception as e:
		ohm2_accounts_light_utils.delete_user(user)
		return {"error" : api_v1_errors.SIGNUP_PIPELINE_FAILED}
	

	res = {
		"error" : None,
		"ret" : True,
	}
	return res



@ohm2_accounts_light_safe_request
def login(request, params):
	p = h_utils.cleaned(params, (
							("string", "username", 1),
							("string", "password", 1),
						))


	if request.user.is_authenticated():
		return {"error": None, "ret" : True}
	
	else:
		username, password = p["username"], p["password"]

		
	if not settings.ENABLE_EMAIL_LOGIN and h_utils.is_email_valid(username):
		return {"error" : api_v1_errors.EMAIL_LOGIN_DISABLED}

	elif settings.ENABLE_EMAIL_LOGIN and h_utils.is_email_valid(username) and ohm2_accounts_light_utils.user_exist(email = username) and settings.UNIQUE_USER_EMAILS:
		user = ohm2_accounts_light_utils.get_user(email = username)
		auth_user = ohm2_accounts_light_utils.user_authenticate(user.get_username(), password)
	
	else:
		auth_user = ohm2_accounts_light_utils.user_authenticate(username, password)
	
	
	if auth_user is None:
		return {"error" : api_v1_errors.WRONG_CREDENTIALS}

	else:
		ohm2_accounts_light_utils.run_login_pipeline(request, auth_user)	
	

	res = {
		"error" : None,
		"ret" : True,
	}
	return res



@ohm2_accounts_light_safe_request
def logout(request, params):
	p = h_utils.cleaned(params,	(
						))


	if not request.user.is_authenticated():
		return {"error": None, "ret" : False}
	
	else:
		ohm2_accounts_light_utils.run_logout_pipeline(request)	
	

	res = {
		"error" : None,
		"ret" : True,
	}
	return res


@ohm2_accounts_light_safe_request
def signup_and_get_token(request, params):
	p = h_utils.cleaned(params, (
							("string", "username", 1),
						))


	username = p["username"]

	res, error = signup(request, params)
	if error:
		return {"error" : error.regroup()}
	
	elif res.get("error"):
		return {"error" : res.get("error")}

	elif not res.get("ret", False):
		return {"error" : api_v1_errors.SIGNUP_FAILED}	

	else:
		user = ohm2_accounts_light_utils.get_user(username = username)

	try:
		token = ohm2_accounts_light_utils.get_or_create_authtoken(user)
	except Exception as e:
		return {"error" : api_v1_errors.SIGNUP_FAILED_DUE_TO_TOKEN}
	
	
	res = {
		"error" : None,
		"ret" : {
			"token" : token.key,
		}
	}
	return res



@ohm2_accounts_light_safe_request
def login_and_get_token(request, params):
	p = h_utils.cleaned(params, (
							("string", "username", 1),
						))


	username = p["username"]

	res, error = login(request, params)
	if error:
		return {"error" : error.regroup()}
	
	elif res.get("error"):
		return {"error" : res.get("error")}

	elif not res.get("ret", False):
		return {"error" : api_v1_errors.LOGIN_FAILED}	

	else:
		user = ohm2_accounts_light_utils.get_user(username = username)

	try:
		token = ohm2_accounts_light_utils.get_or_create_authtoken(user)
	except Exception as e:
		return {"error" : api_v1_errors.LOGIN_FAILED_DUE_TO_TOKEN}
	
	
	res = {
		"error" : None,
		"ret" : {
			"token" : token.key,
		}
	}
	return res



@ohm2_accounts_light_safe_request
def create_authtoken(request, params):
	p = h_utils.cleaned(params,	(
							("string", "username", 1),
						))


	user = ohm2_accounts_light_utils.get_user(username = p["username"])
	token = ohm2_accounts_light_utils.get_or_create_authtoken(user)

	res = {
		"error" : None,
		"ret" : {
			"token" : token.key,
		}
	}
	return res



@ohm2_accounts_light_safe_request
def get_authtoken(request, params):
	p = h_utils.cleaned(params,	(
							("string", "username", 1),
						))


	user = ohm2_accounts_light_utils.get_user(username = p["username"])
	token = ohm2_accounts_light_utils.get_or_create_authtoken(user)

	res = {
		"error" : None,
		"ret" : {
			"token" : token.key,
		}
	}
	return res



@ohm2_accounts_light_safe_request
def send_password_reset_link(request, params):
	p = h_utils.cleaned(params,	(
							("string", "username", 1),
						))


	if request.user.is_authenticated():
		return {"error": None, "ret" : False}

	username = p["username"]

	if h_utils.is_email_valid(username) and settings.UNIQUE_USER_EMAILS:
		user = ohm2_accounts_light_utils.get_or_none_user(email = username)

	else:	
		user = ohm2_accounts_light_utils.get_or_none_user(username = username)
	
	if user is None:
		return {"error": None, "ret" : False}
		
	passwordreset = ohm2_accounts_light_utils.get_or_none_passwordreset(user = user, activation_date = None)
	if passwordreset is None:
		passwordreset = ohm2_accounts_light_utils.create_passwordreset(user)

	
	sent = False
	if passwordreset.send_again() and settings.PASSWORD_RESET_SEND_ENABLE:

		passwordreset, sent = ohm2_accounts_light_utils.send_passwordreset(passwordreset, request)
		


	res = {
		"error" : None,
		"ret" : sent,
	}
	return res



@ohm2_accounts_light_safe_request
def set_password_reset(request, params):
	p = h_utils.cleaned(params,	(
							("string", "username", 1),
							("string", "password", 1),
							("string", "identity", 0),
							("string", "code", 0),
						))


	if request.user.is_authenticated():
		return {"error": None, "ret" : False}

	username, identity, code, password = p["username"], p["identity"], p["code"], p["password"]

	lookup = {}

	if len(identity) > 0:
		lookup["identity"] = identity

	elif len(code) > 0:
		lookup["code__iexact"] = code
	
	else:
		return {"error" : api_v1_errors.PASSWORD_RESET_IDENTITY_AND_CODE_CANT_BE_BOTH_EMPTY}


	if h_utils.is_email_valid(username) and settings.UNIQUE_USER_EMAILS:
		lookup["user__email"] = username

	else:
		lookup["user__username"] = username
	

	passwordreset = ohm2_accounts_light_utils.get_or_none_passwordreset(**lookup)
	if passwordreset is None:
		return {"error" : api_v1_errors.PASSWORD_RESET_INVALID}
	
	elif passwordreset.last_sent_date == None:
		return {"error" : api_v1_errors.PASSWORD_RESET_INVALID}

	elif passwordreset.activation_date != None:
		return {"error" : api_v1_errors.PASSWORD_RESET_ALREADY_ACTIVATED}

	elif settings.CHECK_PASSWORD_SECURE and not ohm2_accounts_light_utils.is_password_secure(password):
		return {"error" : api_v1_errors.THE_PASSWORD_IS_NOT_SECURE}

	else:
		passwordreset = ohm2_accounts_light_utils.change_password_with_passwordreset(passwordreset, password)

		
	res = {
		"error" : None,
		"ret" : True,
	}
	return res



@ohm2_accounts_light_safe_request
def update_user_information(request, params):
	p = h_utils.cleaned(params, (						
							("string", "firstname", 0),
							("string", "lastname", 0),
						))

	
	user = ohm2_accounts_light_utils.get_user(username = request.user.get_username())
	
	user = h_utils.db_update(user, first_name = p["firstname"], last_name = p["lastname"])
	
	ret = {
		"error" : None,
		"ret" : True,
	}
	return ret



def process_social_login_and_get_token(request, username, email, **options):
	user = ohm2_accounts_light_utils.get_or_none_user(username = username)
	if user is None:
		
		password = h_utils.random_string(32)
		params = {
			"username": username,
			"email": email,
			"password": password,
			"user_information": {},
		}
		res, error = signup(request, params, **options)
		if error:
			return {"error" : error.regroup()}
		
		elif res.get("error"):
			return {"error" : res.get("error")}

		elif not res.get("ret", False):
			return {"error" : api_v1_errors.SIGNUP_FAILED}	

		user = ohm2_accounts_light_utils.get_user(username = username)

	token = ohm2_accounts_light_utils.get_or_create_authtoken(user)	
	res = {
		"error" : None,
		"ret" : {
			"username": username,
			"token" : token.key,
		}
	}
	return res




@ohm2_accounts_light_safe_request
def facebook_login_and_get_token(request, params):
	p = h_utils.cleaned(params, (
							("string", "access_token", 10),
						))

	try:
		graph = facebook.GraphAPI(access_token = p["access_token"])
	except Exception as e:
		return {"error" : api_v1_errors.INVALID_FACEBOOK_ACCESS_TOKEN}

		
	try:
		me = graph.get_object(id = "me?fields=" + settings.FACEBOOK_ME_FIELDS)
	except Exception as e:
		return {"error" : api_v1_errors.FACEBOOK_CONNECTION_ERROR}

	email = me.get("email")
	if email is None:
		return {"error" : api_v1_errors.FACEBOOK_EMAIL_PERMISSION_NOT_SETTED}
	
	username = email
	
	options = {
		"facebook": {
			"response": me,
			"kwargs": {},
		}
	}
	return process_social_login_and_get_token(request, username, email, **options)




@ohm2_accounts_light_safe_request
def google_plus_login_and_get_token(request, params):
	p = h_utils.cleaned(params, (
							("string", "access_token", 10),
						))

	
	try:
		r = requests.get(settings.GOOGLE_PLUS_PEOPLE_ME_URL, params = {'access_token': p["access_token"]})
	except Exception as e:
		return {"error" : api_v1_errors.GOOGLE_PLUS_CONNECTION_ERROR}

	
	data = r.json()
	if data.get("error"):
		return {"error" : api_v1_errors.INVALID_GOOGLE_PLUS_ACCESS_TOKEN}
	
	emails = data.get("emails", [])
	if len(emails) == 0:
		return {"error" : api_v1_errors.GOOGLE_PLUS_NO_EMAILS_ASSOCIATED_WITH_THE_ACCOUNT}
	
	username = email = emails[0]["value"]

	options = {}

	"""
	OH: Get image
	"""

	return process_social_login_and_get_token(request, username, email, **options)





