# coding: utf-8
from rest_framework import serializers
from rest_framework.reverse import reverse
from taggit_serializer.serializers import (
    TagListSerializerField,
    TaggitSerializer,
)
from common.serializers import LinkSerializer
from .models import (
    File,
    FileContext,
)


class FileContextSerializer(serializers.ModelSerializer):

    class Meta:
        model = FileContext
        fields = (
            'id',
            'content_type',
            'object_id'
        )


class FileSerializer(TaggitSerializer, LinkSerializer):

    tags = TagListSerializerField()

    context = FileContextSerializer(many=True, read_only=True)

    def get_links(self, obj):

        request = self.context.get('request')
        detailUrl = reverse('file-detail', kwargs={'pk': obj.pk}, request=request)
        return {
            'self': detailUrl,
            'download': detailUrl + '/download',
            'attach': detailUrl + '/attach-from',
            'detach': detailUrl + '/detach-from'
        }

    class Meta:
        model = File
        fields = (
            'id',
            'name',
            'created_by',
            'date_created',
            'date_updated',
            'document',
            'context',
            'tags',
            'links',
        )


class FilesMixInSerializer(object):

    files = FileSerializer(many=True, read_only=True)


class AttachDetachSerializer(serializers.Serializer):
    """
    Serializer that validates and helps
    to construct the required request data
    for attach and detach endpoints
    """

    model_name = serializers.CharField()
    model_id = serializers.IntegerField()

    class Meta:
        fields = '__all__'