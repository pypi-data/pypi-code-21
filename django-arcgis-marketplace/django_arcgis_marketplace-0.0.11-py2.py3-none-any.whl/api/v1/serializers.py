from rest_framework import serializers
from taggit_serializer import serializers as t_serializers

from ... import models
from .. import fields


__all__ = ['AccountSerializer', 'WebMapingAppSerializer']


class AccountBaseSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='id.hex')

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if hasattr(self.Meta, 'extra_fields'):
            for field in self.Meta.extra_fields:
                data[field] = getattr(instance, field)
        return data


class AccountBasicSerializer(AccountBaseSerializer):

    class Meta:
        model = models.Account
        fields = ('id', 'avatar', 'created')
        extra_fields = ('username', 'first_name', 'last_name', 'region')


class AccountSerializer(AccountBaseSerializer):

    class Meta:
        model = models.Account
        fields = ('id', 'avatar', 'created')

    def to_representation(self, instance):
        data = instance.extra
        data.update(super().to_representation(instance))
        return data


class WebMapingAppSerializer(t_serializers.TaggitSerializer,
                             serializers.ModelSerializer):

    owner = AccountBasicSerializer(read_only=True)
    configuration = serializers.JSONField(required=False)
    url_query = serializers.JSONField(required=False)
    preview = fields.PreviewField(required=False)
    tags = t_serializers.TagListSerializerField(required=False)

    class Meta:
        model = models.WebMapingApp
        fields = (
            'owner', 'youtube_url', 'purpose', 'api', 'file', 'preview',
            'configuration', 'url_query', 'tags'
        )

        extra_kwargs = {
            'file': {'write_only': True}
        }
