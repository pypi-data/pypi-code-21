from rest_framework import serializers


from django_framework.django_helpers.serializer_helpers import BaseSerializer
from django_framework.django_helpers.serializer_helpers.serialize_registry import register_serializer
from django_framework.django_helpers.serializer_helpers.serialize_registry import get_serializer


from django_framework.django_helpers.model_helpers.model_registry import get_model

from django_framework.django_helpers.serializer_helpers.serializer_fields import UnixEpochDateTimeField, UnixEpochDateTimeFieldHuman
from django_framework.django_helpers.serializer_helpers.serializer_fields import ChoiceSelectionField, ChoiceSelectionFieldHuman 

import json

class JobSerializer(BaseSerializer):
    run_at = UnixEpochDateTimeField(required=False)
    run_at_alt = UnixEpochDateTimeFieldHuman(source_name = 'run_at')
    
    response_at = UnixEpochDateTimeField(required=False)
    response_at_alt = UnixEpochDateTimeFieldHuman(source_name = 'response_at')
    
    
    completed_at = UnixEpochDateTimeField(required=False)
    completed_at_alt = UnixEpochDateTimeFieldHuman(source_name = 'completed_at')
    
    
    timeout_at = UnixEpochDateTimeField(required=False)
    timeout_at_alt = UnixEpochDateTimeFieldHuman(source_name = 'timeout_at')
    
    
    status = ChoiceSelectionField()
    status_alt = ChoiceSelectionFieldHuman(source_name = 'status')
    
    class Meta:
        
        model = get_model(model_name="Job")
        fields = BaseSerializer.Meta.fields + ["model_name","model_uuid","model_id",
                                               "command","action",
                                               "initial_payload",
                                               "status","status_alt",
                                               "response_payload",
                                               "error_notes",
                                               "job_timeout",
                                               "timeout_at", "timeout_at_alt",
                                               "run_at", "run_at_alt",
                                               "response_at", "response_at_alt",
                                               "completed_at", "completed_at_alt",
                                               "job_type"
                                               ]
        read_only_fields = BaseSerializer.Meta.read_only_fields
        hidden_fields = []


register_serializer(JobSerializer, version= 'default')
