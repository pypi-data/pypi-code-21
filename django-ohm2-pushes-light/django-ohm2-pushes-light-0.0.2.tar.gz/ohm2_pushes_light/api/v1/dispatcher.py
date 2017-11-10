from ohm2_handlers_light import utils as h_utils
from ohm2_pushes_light.decorators import ohm2_pushes_light_safe_request
from ohm2_pushes_light import utils as ohm2_pushes_light_utils
from ohm2_pushes_light import settings
from . import errors as api_v1_errors
from . import settings as api_v1_settings



@ohm2_pushes_light_safe_request
def gateways_onesignal_register_device(request, params, **pipeline_options):
	p = h_utils.cleaned(params, (
							("string", "player_id", 1),
							("string", "push_token", 1),
							("integer", "platform", None),
						))

	user = ohm2_accounts_light_utils.get_user(username = p["username"])
	platform, player_id, push_token = p["platform"], p["player_id"], p["push_token"]

	device = ohm2_pushes_light_utils.onesignal_utils.get_or_none_device(user = user, platform = platform, player_id = player_id)
	if device is None:
		device = ohm2_pushes_light_utils.onesignal_utils.create_device(user, platform, player_id, push_token)
	
	
	res = {
		"error" : None,
		"ret" : True,
	}
	return res




