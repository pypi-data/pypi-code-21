from rest_framework import serializers
import arrow

from django_framework.django_helpers.serializer_helpers import BaseSerializer
from django_framework.django_helpers.serializer_helpers.serialize_registry import register_serializer
from django_framework.django_helpers.serializer_helpers.serialize_registry import get_serializer

from django_framework.django_helpers.serializer_helpers.serializer_fields import ManyToManyIdListField, TripleDesField, UnixEpochDateTimeField
from django_framework.django_helpers.model_helpers.model_registry import get_model
from django.core.exceptions import ValidationError

class BasicProfileRunSerializer(BaseSerializer):
    profile_id = serializers.IntegerField()

    class Meta:
        
        model = get_model(model_name="BasicProfileRun")
        fields = BaseSerializer.Meta.fields + [
            "profile_id", 
        ]
        
        read_only_fields = BaseSerializer.Meta.read_only_fields  # not allowed to edit, will not throw error
        hidden_fields = [] # attempting to PUT to it will error.
        write_once_fields = [] # can only be set upon creation. not editable after
        


register_serializer(BasicProfileRunSerializer, version= 'default')
