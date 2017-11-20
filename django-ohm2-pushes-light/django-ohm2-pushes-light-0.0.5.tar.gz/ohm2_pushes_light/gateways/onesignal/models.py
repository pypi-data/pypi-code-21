from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.utils.translation import ugettext as _
from ohm2_handlers_light.models import BaseModel
from ohm2_pushes_light import models as ohm2_pushes_light_models
from . import managers
from . import settings




class Device(ohm2_pushes_light_models.Device):
	player_id = models.CharField(max_length = settings.STRING_DOUBLE)
	push_token = models.CharField(max_length = settings.STRING_DOUBLE)

	def __str__(self):
		return "[%s][%s][player id: %s]" % (self.user.get_username(), self.platform_str, self.player_id)