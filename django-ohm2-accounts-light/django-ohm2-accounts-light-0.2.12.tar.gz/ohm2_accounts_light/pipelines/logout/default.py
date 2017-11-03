from ohm2_accounts_light import utils as ohm2_accounts_light
import os


def default(request, previous_outputs, *args, **kwargs):
	output = {}
	
	ohm2_accounts_light.user_logout(request)
	
	return output
