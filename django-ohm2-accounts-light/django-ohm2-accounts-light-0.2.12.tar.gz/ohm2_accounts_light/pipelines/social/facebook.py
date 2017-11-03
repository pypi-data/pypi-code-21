from ohm2_accounts_light import utils as ohm2_accounts_light_utils

def login(backend, user, response, *args, **kwargs):
	
	if backend.name == "facebook":
			
		pipeline_options = {
			"facebook": {
				"response": response,
				"kwargs": kwargs,
			},
		}	
		ohm2_accounts_light_utils.run_signup_pipeline(backend.strategy.request, user, **pipeline_options)

	
	return {}