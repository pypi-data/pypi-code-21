from django.contrib.auth.models import User as AuthUser
from rest_framework import serializers
from ohm2_accounts_light import models as ohm2_accounts_light_models



class User(serializers.ModelSerializer):
	class Meta:
		model = AuthUser
		fields = (
			'username',
			'email',
			'last_name',
			'first_name',
		)

