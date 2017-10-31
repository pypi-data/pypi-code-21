from rest_framework import serializers
import arrow

from django_framework.django_helpers.serializer_helpers import BaseSerializer
from django_framework.django_helpers.serializer_helpers.serialize_registry import register_serializer
from django_framework.django_helpers.serializer_helpers.serialize_registry import get_serializer

from django_framework.django_helpers.serializer_helpers.serializer_fields import ManyToManyIdListField, TripleDesField
from django_framework.django_helpers.serializer_helpers.serializer_fields import UnixEpochDateTimeField, UnixEpochDateTimeFieldHuman
from django_framework.django_helpers.serializer_helpers.serializer_fields import ChoiceSelectionField, ChoiceSelectionFieldHuman

from django_framework.django_helpers.model_helpers.model_registry import get_model
from django.core.exceptions import ValidationError

class BasicTestRunSerializer(BaseSerializer):

    basic_profile_run_fk_field_id = serializers.IntegerField()
    
    basic_profile_run_ids = ManyToManyIdListField(source="basic_profile_run", required=False)
    
    epoch_time_field = UnixEpochDateTimeField(required=False)
    epoch_time_field_alt =UnixEpochDateTimeFieldHuman(source_name = 'epoch_time_field')

    encrypted_text_field = TripleDesField(allow_unencrypt = True, required = False)
    encrypted_text_strict_field = TripleDesField(allow_unencrypt = False, required = False)

    choices_field = ChoiceSelectionField()
    choices_field_alt = ChoiceSelectionFieldHuman(source_name = 'choices_field')


    class Meta:
        
        model = get_model(model_name="BasicTestRun")
        fields = BaseSerializer.Meta.fields + [
            "basic_profile_run_fk_field_id",
            "basic_profile_run_ids",
            "normal_text_field", 
            
            "write_once_text_field",
             "read_only_text_field",
            "encrypted_text_field", 
            "encrypted_text_strict_field", 
            "epoch_time_field", "epoch_time_field_alt",
            "choices_field", "choices_field_alt",
        ]
        
        read_only_fields = BaseSerializer.Meta.read_only_fields + ['read_only_text_field']  # not allowed to edit, will not throw error
        hidden_fields = ["hidden_text_field"] # not shown to user
        write_once_fields = ["write_once_text_field"] # can only be set upon creation. not editable after
        


register_serializer(BasicTestRunSerializer, version= 'default')
