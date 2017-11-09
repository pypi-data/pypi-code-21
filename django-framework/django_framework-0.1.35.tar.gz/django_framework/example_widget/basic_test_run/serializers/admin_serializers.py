from django_framework.django_helpers.serializer_helpers import BaseSerializer
from django_framework.django_helpers.serializer_helpers.serialize_registry import register_serializer
from django_framework.django_helpers.serializer_helpers.serialize_registry import get_serializer


from django_framework.django_helpers.model_helpers.model_registry import get_model

from rest_framework import serializers

# BasicTestRunSerializer = get_serializer(serializer_name = 'BasicTestRunSerializer')
from default_serializers import BasicTestRunSerializer # this needs to be done so that BasicTestRunSerializer is loaded first

class AdminBasicTestRunSerializer(BasicTestRunSerializer):

    class Meta:
        
        model = get_model(model_name="BasicTestRun")
        fields = BaseSerializer.Meta.fields + [
            "basic_profile_run_fk_field_id",
            "basic_profile_run_ids",
            "normal_text_field", 
            "hidden_text_field",
            "write_once_text_field",
             "read_only_text_field", 
            "encrypted_text_field", 
            "encrypted_text_strict_field", 
            "epoch_time_field", "epoch_time_field_alt",
            "choices_field", "choices_field_alt",
        ]
        
        read_only_fields = BaseSerializer.Meta.read_only_fields  # not allowed to edit, will not throw error
        hidden_fields = [] # attempting to PUT to it will error.
        write_once_fields = [] # can only be set upon creation. not editable after
        



register_serializer(AdminBasicTestRunSerializer, version= 'admin')