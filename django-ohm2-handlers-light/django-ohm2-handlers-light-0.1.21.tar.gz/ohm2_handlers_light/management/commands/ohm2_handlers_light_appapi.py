from django.core.management.base import BaseCommand, CommandError
from ohm2_handlers_light import utils as h_utils
from subprocess import call
import os, shutil


def load_template(template, name, version):
	path = os.path.join( os.path.dirname(os.path.realpath(__file__)), template)

	with open(path, "r") as f:
		content = f.read()

		
	return content.format(name.upper(),
						  name.lower(),
						  name.title(),
						  h_utils.get_random_string(32),
						  int(h_utils.random_string_hexdigits(3), 16) * 2**6,
						  version)


def append(filename, text):
	with open(filename, "a") as f:
		f.write(text)

def override(filename, text):
	with open(filename, "w") as f:
		f.write(text)


class Command(BaseCommand):
	
	def add_arguments(self, parser):
		parser.add_argument('-s', '--source')
		parser.add_argument('-a', '--app')
		parser.add_argument('-p', '--prefixfolder', action='store_true', dest = "prefixfolder", default = False)

	def handle(self, *args, **options):
		source = options["source"]
		app = options["app"]
		create_api_folder = options.get("prefixfolder")
		
		base_dst = os.path.join(source, app)
		if create_api_folder:
			base_dst = os.path.join(base_dst, "api")
		

		api_versions = ["v1"]
		for version in api_versions:
			dst = os.path.join(base_dst, version)
			
			os.makedirs(dst)

			to_run = [
				{"src" : "templates/appapi_urls.template", "dst" : os.path.join(dst, "urls.py"), "func" : override},
				{"src" : "templates/appapi_views.template", "dst" : os.path.join(dst, "views.py"), "func" : override},
				{"src" : "templates/appapi_dispatcher.template", "dst" : os.path.join(dst, "dispatcher.py"), "func" : override},
				{"src" : "templates/appapi_decorators.template", "dst" : os.path.join(dst, "decorators.py"), "func" : override},
				{"src" : "templates/appapi_errors.template", "dst" : os.path.join(dst, "errors.py"), "func" : override},
				{"src" : "templates/appapi_definitions.template", "dst" : os.path.join(dst, "definitions.py"), "func" : override},
				{"src" : "templates/appapi_utils.template", "dst" : os.path.join(dst, "utils.py"), "func" : override},
				{"src" : "templates/appapi_serializers.template", "dst" : os.path.join(dst, "serializers.py"), "func" : override},
				{"src" : "templates/appapi_settings.template", "dst" : os.path.join(dst, "settings.py"), "func" : override},
			]
			for run in to_run:
				text = load_template(run["src"], app, version)
				run["func"](run["dst"], text)

				

		

		




		