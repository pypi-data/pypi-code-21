from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from ohm2_handlers_light import utils as h_utils
from ohm2_countries_light import utils as ohm2_countries_light_utils
from ohm2_countries_light import settings
import os, pycountry

class Command(BaseCommand):
	
	def add_arguments(self, parser):
		parser.add_argument('-f', '--flags',
							action = 'store_true',
							default = False)

	def handle(self, *args, **options):
		flags = options["flags"]
		
		
		for c in pycountry.countries:

			if flags:
				flag_small_dst_path = os.path.join(settings.FLAGS_SMALL_BASE_PATH, c.alpha_2.lower() + ".png")
				flag_small_exist = os.path.isfile(flag_small_dst_path)
				if flag_small_exist:
					flag_small = h_utils.new_local_file(flag_small_dst_path)
				else:
					flag_small = None

			else:
				flag_small = None		

			
			official_name = getattr(c, "official_name", c.name)
			country = ohm2_countries_light_utils.get_or_none_country(alpha_3 = c.alpha_3)
			if country is None:
				country = ohm2_countries_light_utils.create_country(c.name, official_name, c.alpha_2, c.alpha_3, c.numeric,
													  				flag_small = flag_small)
			else:
				country = ohm2_countries_light_utils.update_country(country, flag_small = flag_small)
			
			
				


		
			


			