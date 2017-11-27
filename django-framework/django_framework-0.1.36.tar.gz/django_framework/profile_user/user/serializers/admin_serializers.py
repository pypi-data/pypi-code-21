from django_framework.django_helpers.serializer_helpers import BaseSerializer
from django_framework.django_helpers.serializer_helpers.serialize_registry import register_serializer
from django_framework.django_helpers.serializer_helpers.serialize_registry import get_serializer


from django_framework.django_helpers.model_helpers.model_registry import get_model

from rest_framework import serializers

# ProfileSerializer = get_serializer(serializer_name = 'ProfileSerializer')
from default_serializers import UserSerializer # this needs to be done so that ProfileSerializer is loaded first

from django.contrib.auth.models import User

class AdminUserSerializer(UserSerializer):

    class Meta:
        
        model = get_model(model_name="User")
        fields =  ["username", "first_name","last_name","email","password","is_staff","is_active","is_superuser","last_login","date_joined"]
        
        read_only_fields = ["id"]  # not allowed to edit, will not throw error
        hidden_fields = [] # attempting to PUT to it will error.
        write_once_fields = [] # can only be set upon creation. not editable after

register_serializer(AdminUserSerializer, version= 'admin')