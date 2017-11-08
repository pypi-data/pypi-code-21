from ohm2_handlers_light import utils as h_utils
from ohm2_accounts_light import utils as ohm2_accounts_light_utils

def user_information(request, user, previous_outputs, *args, **kwargs):
	output = {}
	
	user_information = kwargs.get("ohm2_user_information", {})
	if user_information:
		
		first_name, last_name = user_information["first_name"], user_information["last_name"]
		
		if first_name:
			user.first_name = first_name
		
		if last_name:
			user.last_name = last_name		
		

		user.save()

	return (user, output)
