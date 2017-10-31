from rest_framework import serializers


from django_framework.django_helpers.serializer_helpers import BaseSerializer
from django_framework.django_helpers.serializer_helpers.serialize_registry import register_serializer
from django_framework.django_helpers.serializer_helpers.serialize_registry import get_serializer

from django_framework.django_helpers.serializer_helpers.serializer_fields import ManyToManyIdListField, TripleDesField
from django_framework.django_helpers.model_helpers.model_registry import get_model
from django.core.exceptions import ValidationError


from django.contrib.auth.models import User


class UserSerializer(BaseSerializer):
    
    def validate_password(self, data):
        
        if len(data) < 6:
            raise ValidationError('The length of a password must be greater than 6')
        return data
    
    class Meta:
        
        model = get_model(model_name="User")
        fields = ["id", "username", "first_name","last_name","email","is_staff","is_active","is_superuser","last_login","date_joined"]
        read_only_fields = ["id", "username", "first_name","last_name","email","is_staff","is_active","is_superuser","last_login","date_joined"]  # not allowed to edit, will not throw error
        hidden_fields = ["password"] 
        write_once_fields = [] # can only be set upon creation. not editable after
        


register_serializer(UserSerializer, version= 'default')
