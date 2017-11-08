from ohm2_accounts_light import utils as ohm2_accounts_light
import os


def default(request, auth_user, previous_outputs, *args, **kwargs):
	output = {}
	
	ohm2_accounts_light.user_login(request, auth_user)
	
	return (auth_user, output)
