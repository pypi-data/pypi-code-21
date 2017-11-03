from django.apps import apps
from ohm2_accounts_light import utils as ohm2_accounts_light


def user_avatar(request, user, previous_outputs, *args, **kwargs):
	output = {}
	
	#avatar = apps.get_model()
	
	return (user, output)
