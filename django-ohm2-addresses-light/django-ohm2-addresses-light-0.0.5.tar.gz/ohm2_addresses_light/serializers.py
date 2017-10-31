from rest_framework import serializers
from drf_extra_fields.geo_fields import PointField
from ohm2_countries_light import serializers as ohm2_countries_light_serializers
from . import models as ohm2_addresses_light_models
from . import settings



class Address(serializers.ModelSerializer):

	country = ohm2_countries_light_serializers.Country()
	coordinates = PointField()
	
	class Meta:
		model = ohm2_addresses_light_models.Address
		fields = (
			'identity',
			'created',
			'last_update',
			'country',
			'first_level',
			'second_level',
			'third_level',
			'fourth_level',
			'street',
			'number',
			'coordinates',
		)
