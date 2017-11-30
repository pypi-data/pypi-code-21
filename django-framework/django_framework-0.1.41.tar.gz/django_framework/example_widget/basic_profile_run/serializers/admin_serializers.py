from django_framework.django_helpers.serializer_helpers import BaseSerializer
from django_framework.django_helpers.serializer_helpers.serialize_registry import register_serializer
from django_framework.django_helpers.serializer_helpers.serialize_registry import get_serializer


from django_framework.django_helpers.model_helpers.model_registry import get_model

from rest_framework import serializers

# BasicProfileRunSerializer = get_serializer(serializer_name = 'BasicProfileRunSerializer')
from default_serializers import BasicProfileRunSerializer # this needs to be done so that BasicProfileRunSerializer is loaded first

class AdminBasicProfileRunSerializer(BasicProfileRunSerializer):
    pass

register_serializer(AdminBasicProfileRunSerializer, version= 'admin')