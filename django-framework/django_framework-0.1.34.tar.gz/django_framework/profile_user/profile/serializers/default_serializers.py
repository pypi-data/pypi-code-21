from rest_framework import serializers


from django_framework.django_helpers.serializer_helpers import BaseSerializer
from django_framework.django_helpers.serializer_helpers.serialize_registry import register_serializer
from django_framework.django_helpers.serializer_helpers.serialize_registry import get_serializer

from django_framework.django_helpers.serializer_helpers.serializer_fields import ManyToManyIdListField, TripleDesField
from django_framework.django_helpers.model_helpers.model_registry import get_model
from django.core.exceptions import ValidationError

class ProfileSerializer(BaseSerializer):
    
    user_id = serializers.IntegerField()
    
    def validate_username(self, data):
        username = data
        
        username = username.strip().lower()
        # check uniqueness!
        if self.Meta.model.objects.filter(username=username).count() > 0:
            raise ValidationError('The username must be unique!')
        
        if len(username) < 6:
            raise ValidationError('The username length must be greater than 6')
        
        return username

    class Meta:
        
        model = get_model(model_name="Profile")
        fields = BaseSerializer.Meta.fields + [
            "username", "email", "first_name", "last_name", "user_id"
        ]
        
        read_only_fields = BaseSerializer.Meta.read_only_fields  # not allowed to edit, will not throw error
        hidden_fields = ["security_code", "security_code_valid_until"] # attempting to PUT to it will error.
        write_once_fields = [] # can only be set upon creation. not editable after
        


register_serializer(ProfileSerializer, version= 'default')
