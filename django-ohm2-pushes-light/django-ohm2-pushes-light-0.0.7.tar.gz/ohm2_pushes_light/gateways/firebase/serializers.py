from rest_framework import serializers
from . import models as firebase_models
from . import settings


"""
class Serializer(serializers.ModelSerializer):
	class Meta:
		model = firebase_models.Model
		fields = (
			'identity',
			'created',
			'last_update',
		)
"""		