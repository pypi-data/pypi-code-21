from ohm2_handlers_light.decorators import ohm2_handlers_light_safe_request

def ohm2_pushes_light_safe_request(function):
	return ohm2_handlers_light_safe_request(function, "ohm2_pushes_light")
