from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.utils.translation import ugettext as _
from ohm2_handlers_light.models import BaseModel
from ohm2_handlers_light import utils as h_utils
from . import managers
from . import settings



class PasswordReset(BaseModel):
	user = models.ForeignKey(User)

	last_sent_date = models.DateTimeField(null = True, blank = True, default = None)
	activation_date = models.DateTimeField(null = True, blank = True, default = None)
	ip_address = models.GenericIPAddressField(null = True, blank = True, default = "")
	code = models.CharField(max_length = settings.STRING_NORMAL, unique = True)


	def send_again(self):
		if self.last_sent_date and not h_utils.is_older_than_now(self.last_sent_date, seconds = settings.MINIMUM_PASSWORD_RESET_DELAY):
			return False
		return True

	def __str__(self):
		return self.user.username