from ohm2_accounts_light import utils as ohm2_accounts_light_utils

def login(backend, user, response, *args, **kwargs):
	
	if backend.name == "google-oauth2":
		
		pipeline_options = {
			"google_plus": {
				"response": response,
				"kwargs": kwargs,
			},
		}	
		ohm2_accounts_light_utils.run_signup_pipeline(backend.strategy.request, user, **pipeline_options)
		

	
	return {}