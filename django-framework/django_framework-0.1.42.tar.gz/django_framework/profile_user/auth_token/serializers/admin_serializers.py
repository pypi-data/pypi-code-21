from django_framework.django_helpers.serializer_helpers import BaseSerializer
from django_framework.django_helpers.serializer_helpers.serialize_registry import register_serializer
from django_framework.django_helpers.serializer_helpers.serialize_registry import get_serializer


from django_framework.django_helpers.model_helpers.model_registry import get_model


from default_serializers import AuthTokenSerializer
class AdminAuthTokenSerializer(AuthTokenSerializer):

    class Meta:
        
        model = get_model(model_name="AuthToken")
        fields = BaseSerializer.Meta.fields + [ 
            "user_id",
            "current_token", "expire_at"
        ]
        
        read_only_fields = BaseSerializer.Meta.read_only_fields  # not allowed to edit, will not throw error
        hidden_fields = [] # attempting to PUT to it will error.
        write_once_fields = [] # can only be set upon creation. not editable after

register_serializer(AdminAuthTokenSerializer, version= 'admin')