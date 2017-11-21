from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from ohm2_handlers_light import utils as h_utils
from ohm2_handlers_light import models as handlers_models
from ohm2_handlers_light.definitions import RunException

class Command(BaseCommand):
	
	def add_arguments(self, parser):
		pass #parser.add_argument('-f', '--foo')

	def handle(self, *args, **options):
		# foo = options["foo"]
		
		"""
		be = h_utils.db_create(handlers_models.BaseError, last_update = timezone.now())

		print(be.identity)

		"""

		

		"""
		e = RunException(code = 123, message = "aasdasdsdsd")
		print(e)

		"""

		from Crypto import Random
		from Crypto.Cipher import AES
		import base64

		key_16, iv_16 = h_utils.random_string(16), base64.b64encode(Random.new().read(AES.block_size))


		message = h_utils.random_string(16)

		encrypted = h_utils.encrypt_aes_cfb(key_16, iv_16, message)

		print(encrypted.hex())

		print(message, h_utils.decrypt_aes_cfb(key_16, iv_16, encrypted))