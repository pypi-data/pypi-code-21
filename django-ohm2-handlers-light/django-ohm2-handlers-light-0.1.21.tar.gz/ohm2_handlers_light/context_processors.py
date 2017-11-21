from ohm2_handlers_light import utils as h_utils

def context(request):
	return {"c_ohm2_handlers_light" : h_utils.get_context(request)}