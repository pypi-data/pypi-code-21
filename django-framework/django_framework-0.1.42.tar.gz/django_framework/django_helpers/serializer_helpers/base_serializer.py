import arrow
from rest_framework import serializers

from django_framework.django_helpers.model_helpers.model_registry import get_model_name

from serializer_fields import UnixEpochDateTimeField, UnixEpochDateTimeFieldHuman
from serializer_validators import WriteOnceFieldsValidator


class BaseSerializer(serializers.ModelSerializer):

    last_updated = UnixEpochDateTimeField(required=False)
    created_at = UnixEpochDateTimeField(required=False)

    last_updated_alt = UnixEpochDateTimeFieldHuman(source_name='last_updated')
    created_at_alt   = UnixEpochDateTimeFieldHuman(source_name='created_at')
    
    type = serializers.SerializerMethodField() 

    def to_representation(self, obj):
        # get the original representation
        ret = super(BaseSerializer, self).to_representation(obj)
        
        # remove all hidden field parameters! 
        # this allows things to be written, but does not show up in the serializer
        if getattr(self.Meta, "hidden_fields", None):
            for hidden_field in getattr(self.Meta, "hidden_fields", []):
                ret.pop(hidden_field, None)
        return ret 

    def get_type(self, obj):
        model_name = None
        if obj:
            full_name, model_name = get_model_name(model=obj)
        return model_name

    def get_validators(self):
        # we must override this method because setting validators
        # causes Django Rest Framework to not load it's standard
        # validators
        response = super(BaseSerializer, self).get_validators()  # get parent serializers
        hidden_fields = getattr(self.Meta, "hidden_fields", None)
        write_once_fields = getattr(self.Meta, "write_once_fields", None)

        additional_validators = []


        # check for write_once fields, if so add WriteOnceFieldsValidator
        # to class-level validators
        if write_once_fields is not None:
            additional_validators.append(WriteOnceFieldsValidator(fields=write_once_fields))

        # if any additonal validators, add to response
        if additional_validators:
            response += tuple(additional_validators)

        return response


    class Meta:
        
        fields = [
            "id", "type",
            "uuid",

            "created_at", "created_at_alt", "last_updated", "last_updated_alt",
        ]
        read_only_fields = ["id", "type", "uuid", "last_updated", "created_at"]
        hidden_fields = []
        write_once_fields = ["id", "type", "uuid", "created_at"] # can only be set upon creation. not editable after
        
