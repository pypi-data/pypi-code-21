from ohm2_handlers_light import utils as h_utils
from ohm2_accounts_light.decorators import ohm2_accounts_light_safe_request
from ohm2_accounts_light import utils as ohm2_accounts_light_utils
from ohm2_accounts_light import settings
from . import errors




@ohm2_accounts_light_safe_request
def logout(request, params):
	p = h_utils.cleaned(params,	(
							("string", "next", 1),
						))


	ohm2_accounts_light_utils.user_logout(request)
	

	res = {
		"ret" : p["next"],
	}
	return res