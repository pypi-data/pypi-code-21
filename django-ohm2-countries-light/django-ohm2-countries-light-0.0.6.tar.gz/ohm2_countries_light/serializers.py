from rest_framework import serializers
from . import models as ohm2_countries_light_models
from . import settings



class Country(serializers.ModelSerializer):
	class Meta:
		model = ohm2_countries_light_models.Country
		fields = (
			'identity',
			'created',
			'last_update',
			'name',
			'official_name',
			'alpha_2',
			'alpha_3',
			'numeric',
			'flag_small_url',
		)
