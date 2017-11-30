from django_framework.django_helpers.serializer_helpers import BaseSerializer
from django_framework.django_helpers.serializer_helpers.serialize_registry import register_serializer
from django_framework.django_helpers.serializer_helpers.serialize_registry import get_serializer


from django_framework.django_helpers.model_helpers.model_registry import get_model


# PollSerializer = get_serializer(serializer_name = 'PollSerializer')
from default_serializers import JobSerializer # this needs to be done so that PollSerializer is loaded first

class AdminJobSerializer(JobSerializer):
    
    pass


register_serializer(AdminJobSerializer, version= 'admin')