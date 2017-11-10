from rest_framework import serializers
from . import models as onesignal_models
from . import settings


"""
class Serializer(serializers.ModelSerializer):
	class Meta:
		model = onesignal_models.Model
		fields = (
			'identity',
			'created',
			'last_update',
		)
"""		