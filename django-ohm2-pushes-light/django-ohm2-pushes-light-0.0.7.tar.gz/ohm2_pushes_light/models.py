from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.utils.translation import ugettext as _
from ohm2_handlers_light.models import BaseModel
from . import managers
from . import settings




class Message(BaseModel):
	user = models.ForeignKey(User, on_delete = models.CASCADE)	
	title = models.CharField(max_length = settings.STRING_NORMAL)
	body = models.TextField()	
	data = JSONField(null = True, blank = True, default = {})
	read = models.BooleanField(default = False)
	
	def __str__(self):
		return "%s -> [%s] at [%s]" % (self.title, self.user.get_username(), self.created)

	def get_onesignal_data(self):
		return {
			"body": self.body,
			"data": self.data,
		}

	
				
	


class Device(BaseModel):
	user = models.ForeignKey(User, on_delete = models.CASCADE)

	platform_ios = (1, "iOS")
	platform_android = (2, "Android")
	platform_browser = (3, "Browser")
	
	platforms = (
		platform_ios,
		platform_android,
		platform_browser,
	)
	platform = models.IntegerField(choices = platforms)

	gateway_onesignal = settings.GATEWAY_ONESIGNAL
	gateway_firebase = settings.GATEWAY_FIREBASE
	gateways = settings.GATEWAYS
	gateway = models.IntegerField(choices = gateways, default = settings.DEFAULT_GATEWAY[0])
	
	class Meta:
		abstract = True

	@property
	def is_ios(self):
		return self.platform == self.platform_ios[0]

	@property
	def is_android(self):
		return self.platform == self.platform_android[0]

	@property
	def is_browser(self):
		return self.platform == self.platform_browser[0]		

	@property
	def is_onesignal(self):
		return self.gateway == self.gateway_onesignal[0]

	@property
	def platform_str(self):
		for platform in self.platforms:
			if platform[0] == self.platform:
				return platform[1]
		return ""