from django.conf import settings
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.core.management import call_command
from django.utils import timezone
from rest_framework.test import APIClient
from ohm2_handlers_light import utils as h_utils
from ohm2_accounts_light import utils as ohm2_accounts_light_utils
from ohm2_accounts_light import settings

try:
	import simplejson as json
except Exception:
	import json


							 	
class ApiTestCase(TestCase):
	
	test_username = "testusername"
	test_email = "oliver@ohm2.cl"
	test_password = h_utils.random_string(10)
	
		
	def setUp(self):
		
		user = ohm2_accounts_light_utils.create_user(self.test_username, self.test_email, self.test_password)		
		

	def test_signup_success(self):
		SIGNUPS_ENABLED_ORIGINAL = settings.SIGNUPS_ENABLED
		settings.SIGNUPS_ENABLED = True	

		c = APIClient()
		url = reverse("ohm2_accounts_light:api_v1:signup")
		
		data = {
			"username" : h_utils.random_string(10),
			"password" : h_utils.random_string(10),
		}
		response = c.post(url, data, format = 'json')
		self.assertEqual(response.status_code, 200)

		res = response.json()
		error = True if res["error"] else False
		if error:
			print(res["error"])

		self.assertEqual(error, False)
		settings.SIGNUPS_ENABLED = SIGNUPS_ENABLED_ORIGINAL
		
	
	def test_login_fail(self):
		
		c = APIClient()
		url = reverse("ohm2_accounts_light:api_v1:login")
		
		data = {
			"username" : self.test_username,
			"password" : h_utils.random_string(10),
		}
		response = c.post(url, data, format = 'json')
		self.assertEqual(response.status_code, 200)

		res = response.json()
		error = True if res["error"] else False
		
		self.assertEqual(error, True)	
	

	def test_login_success(self):
		
		c = APIClient()
		url = reverse("ohm2_accounts_light:api_v1:login")
		
		data = {
			"username" : self.test_username,
			"password" : self.test_password,
		}
		response = c.post(url, data, format = 'json')
		self.assertEqual(response.status_code, 200)

		res = response.json()
		error = True if res["error"] else False
		if error:
			print(res["error"])

		self.assertEqual(error, False)

	
	def test_logout_success(self):
		
		c = APIClient()
		c.login(username = self.test_username, password = self.test_password)

		url = reverse("ohm2_accounts_light:api_v1:logout")
		
		data = {
		}

		response = c.post(url, data, format = 'json')
		self.assertEqual(response.status_code, 200)

		res = response.json()
		error = True if res["error"] else False
		if error:
			print(res["error"])

		self.assertEqual(error, False)		


	def test_signup_and_get_token_success(self):
		SIGNUPS_ENABLED_ORIGINAL = settings.SIGNUPS_ENABLED
		settings.SIGNUPS_ENABLED = True	

		c = APIClient()
		url = reverse("ohm2_accounts_light:api_v1:signup_and_get_token")
		
		data = {
			"username" : h_utils.random_string(10),
			"password" : h_utils.random_string(10),
		}
		response = c.post(url, data, format = 'json')
		self.assertEqual(response.status_code, 200)

		res = response.json()
		error = True if res["error"] else False
		if error:
			print(res["error"])

		self.assertEqual(error, False)	
		settings.SIGNUPS_ENABLED = SIGNUPS_ENABLED_ORIGINAL	
	

	def test_login_and_get_token_fail(self):
		
		c = APIClient()
		url = reverse("ohm2_accounts_light:api_v1:login_and_get_token")
		
		data = {
			"username" : self.test_username,
			"password" : h_utils.random_string(10),
		}
		response = c.post(url, data, format = 'json')
		self.assertEqual(response.status_code, 200)

		res = response.json()
		error = True if res["error"] else False
		self.assertEqual(error, True)

	def test_login_and_get_token_success(self):
		
		c = APIClient()
		url = reverse("ohm2_accounts_light:api_v1:login_and_get_token")
		
		data = {
			"username" : self.test_username,
			"password" : self.test_password,
		}
		response = c.post(url, data, format = 'json')
		self.assertEqual(response.status_code, 200)

		res = response.json()
		error = True if res["error"] else False
		if error:
			print(res["error"])

		self.assertEqual(error, False)
		

	def test_send_password_reset_link_already_authenticated_failed(self):
		
		c = APIClient()
		c.login(username = self.test_username, password = self.test_password)

		url = reverse("ohm2_accounts_light:api_v1:send_password_reset_link")
		
		data = {
			"username" : self.test_username,
		}

		response = c.post(url, data, format = 'json')
		self.assertEqual(response.status_code, 200)

		res = response.json()
		error = True if res["error"] else False
		if error:
			print(res["error"])

		ret = res["ret"]

		self.assertEqual(error, ret)

	
	def test_send_password_reset_link_success(self):
		
		c = APIClient()
		
		url = reverse("ohm2_accounts_light:api_v1:send_password_reset_link")
		
		data = {
			"username" : self.test_username,
		}

		response = c.post(url, data, format = 'json')
		self.assertEqual(response.status_code, 200)

		res = response.json()
		error = True if res["error"] else False
		if error:
			print(res["error"])

		self.assertEqual(error, False)
		ret = res["ret"]

		self.assertEqual(ret, True)



	def test_set_password_reset_by_identity_success(self):
			
		self.test_send_password_reset_link_success()

		passwordreset = ohm2_accounts_light_utils.get_passwordreset(user__username = self.test_username, activation_date = None)

		c = APIClient()
		
		url = reverse("ohm2_accounts_light:api_v1:set_password_reset")
		
		data = {
			"username" : self.test_username,
			"password" : h_utils.random_string(10),
			"identity" : passwordreset.identity,
		}

		response = c.post(url, data, format = 'json')
		self.assertEqual(response.status_code, 200)

		res = response.json()
		error = True if res["error"] else False
		if error:
			print(res["error"])

		self.assertEqual(error, False)
		ret = res["ret"]

		self.assertEqual(ret, True)


	def test_set_password_reset_by_code_success(self):
			
		self.test_send_password_reset_link_success()

		passwordreset = ohm2_accounts_light_utils.get_passwordreset(user__username = self.test_username, activation_date = None)

		c = APIClient()
		
		url = reverse("ohm2_accounts_light:api_v1:set_password_reset")
		
		data = {
			"username" : self.test_username,
			"password" : h_utils.random_string(10),
			"code" : passwordreset.code,
		}

		response = c.post(url, data, format = 'json')
		self.assertEqual(response.status_code, 200)

		res = response.json()
		error = True if res["error"] else False
		if error:
			print(res["error"])

		self.assertEqual(error, False)
		ret = res["ret"]

		self.assertEqual(ret, True)


	def test_set_password_reset_by_code_fail(self):
			
		self.test_send_password_reset_link_success()

		passwordreset = ohm2_accounts_light_utils.get_passwordreset(user__username = self.test_username, activation_date = None)
		passwordreset = h_utils.db_update(passwordreset, activation_date = timezone.now())


		
		c = APIClient()
		
		url = reverse("ohm2_accounts_light:api_v1:set_password_reset")
		
		data = {
			"username" : self.test_username,
			"password" : h_utils.random_string(10),
			"code" : passwordreset.code,
		}

		response = c.post(url, data, format = 'json')
		self.assertEqual(response.status_code, 200)

		res = response.json()
		error = True if res["error"] else False
		
		self.assertEqual(error, True)

				

	

	def test_set_password_reset_and_get_token_by_identity_success(self):
			
		self.test_send_password_reset_link_success()

		passwordreset = ohm2_accounts_light_utils.get_passwordreset(user__username = self.test_username, activation_date = None)

		c = APIClient()
		
		url = reverse("ohm2_accounts_light:api_v1:set_password_reset_and_get_token")
		
		data = {
			"username" : self.test_username,
			"password" : h_utils.random_string(10),
			"identity" : passwordreset.identity,
		}

		response = c.post(url, data, format = 'json')
		self.assertEqual(response.status_code, 200)

		res = response.json()
		error = True if res["error"] else False
		if error:
			print(res["error"])

		self.assertEqual(error, False)
		ret = res["ret"]

		has_token = True if ret["token"] else False

		self.assertEqual(has_token, True)

	def test_update_user_information_success(self):
			
		c = APIClient()
		c.login(username = self.test_username, password = self.test_password)

		url = reverse("ohm2_accounts_light:api_v1:update_user_information")
		
		data = {
			"firstname" : h_utils.random_string(10),
			"lastname" : h_utils.random_string(10),
		}

		response = c.post(url, data, format = 'json')
		self.assertEqual(response.status_code, 200)

		res = response.json()
		error = True if res["error"] else False
		if error:
			print(res["error"])

		ret = res["ret"]

		self.assertEqual(error, not ret)	

		
	def test_signup_user_information_success(self):
		SIGNUPS_ENABLED_ORIGINAL = settings.SIGNUPS_ENABLED
		settings.SIGNUPS_ENABLED = True	

		c = APIClient()
		url = reverse("ohm2_accounts_light:api_v1:signup")
		
		data = {
			"username" : h_utils.random_string(10),
			"password" : h_utils.random_string(10),
			"user_info": {
				"first_name": h_utils.random_string(10),
				"last_name": h_utils.random_string(10),
			}
		}
		response = c.post(url, data, format = 'json')
		self.assertEqual(response.status_code, 200)

		res = response.json()
		error = True if res["error"] else False
		if error:
			print(res["error"])

		self.assertEqual(error, False)
		settings.SIGNUPS_ENABLED = SIGNUPS_ENABLED_ORIGINAL	