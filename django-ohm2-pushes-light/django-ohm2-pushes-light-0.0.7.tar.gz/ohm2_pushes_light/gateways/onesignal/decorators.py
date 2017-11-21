from ohm2_handlers_light.decorators import ohm2_handlers_light_safe_request

def onesignal_safe_request(function):
	return ohm2_handlers_light_safe_request(function, "onesignal")
