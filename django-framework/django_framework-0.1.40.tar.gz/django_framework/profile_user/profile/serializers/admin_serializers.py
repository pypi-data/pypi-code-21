from django_framework.django_helpers.serializer_helpers import BaseSerializer
from django_framework.django_helpers.serializer_helpers.serialize_registry import register_serializer
from django_framework.django_helpers.serializer_helpers.serialize_registry import get_serializer


from django_framework.django_helpers.model_helpers.model_registry import get_model

from rest_framework import serializers

# ProfileSerializer = get_serializer(serializer_name = 'ProfileSerializer')
from default_serializers import ProfileSerializer # this needs to be done so that ProfileSerializer is loaded first

class AdminProfileSerializer(ProfileSerializer):

    user_id = serializers.IntegerField()
    
    class Meta:
        
        model = get_model(model_name="Profile")
        fields = BaseSerializer.Meta.fields + [
            "user_id", "username", "email", "first_name", "last_name", "security_code", "security_code_valid_until"
        ]
        
        read_only_fields = BaseSerializer.Meta.read_only_fields  # not allowed to edit, will not throw error
        hidden_fields = [] # attempting to PUT to it will error.
        write_once_fields = [] # can only be set upon creation. not editable after
        



register_serializer(AdminProfileSerializer, version= 'admin')