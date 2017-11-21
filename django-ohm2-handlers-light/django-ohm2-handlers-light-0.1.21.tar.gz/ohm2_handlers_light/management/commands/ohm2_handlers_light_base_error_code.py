from django.core.management.base import BaseCommand, CommandError
from ohm2_handlers_light import utils as h_utils
from subprocess import call
import os

class Command(BaseCommand):
	
	def add_arguments(self, parser):
		pass#parser.add_argument('-l', '--length')


	def handle(self, *args, **options):
		
		#length = options["length"]
		
		self.stdout.write("{0}".format(h_utils.get_base_error_code()))

		




		