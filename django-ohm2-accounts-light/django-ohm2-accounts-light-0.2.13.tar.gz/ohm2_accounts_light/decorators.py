from ohm2_handlers_light.decorators import ohm2_handlers_light_safe_request

def ohm2_accounts_light_safe_request(function):
	return ohm2_handlers_light_safe_request(function, "accounts")
