from rest_framework import serializers


from django_framework.django_helpers.serializer_helpers import BaseSerializer
from django_framework.django_helpers.serializer_helpers.serialize_registry import register_serializer
from django_framework.django_helpers.serializer_helpers.serialize_registry import get_serializer

from django_framework.django_helpers.serializer_helpers.serializer_fields import ManyToManyIdListField, TripleDesField
from django_framework.django_helpers.model_helpers.model_registry import get_model
from django.core.exceptions import ValidationError

from django_framework.django_helpers.serializer_helpers.serializer_fields import UnixEpochDateTimeField, UnixEpochDateTimeFieldHuman

class AuthTokenSerializer(BaseSerializer):
    user_id = serializers.IntegerField()
    expire_at = UnixEpochDateTimeField(required=False)
    expire_at_alt = UnixEpochDateTimeField(required=False)
    
    
    class Meta:
        
        model = get_model(model_name="AuthToken")
        
        fields = BaseSerializer.Meta.fields + [
            "current_token", "expire_at", "expire_at_alt", "user_id"
        ]
        
        read_only_fields = BaseSerializer.Meta.read_only_fields + ["current_token", "expire_at","user_id"]  # not allowed to edit, will not throw error
        hidden_fields = [] # attempting to PUT to it will error.
        write_once_fields = [] # can only be set upon creation. not editable after
        
register_serializer(AuthTokenSerializer, version= 'default')
