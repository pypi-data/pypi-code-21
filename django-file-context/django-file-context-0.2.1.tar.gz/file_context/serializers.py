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


class BasicFileSerializer(TaggitSerializer, LinkSerializer):

    tags = TagListSerializerField()

    def get_links(self, obj):

        request = self.context.get('request')
        detailUrl = reverse('file-detail', kwargs={'pk': obj.pk}, request=request)
        return {
            'self': detailUrl,
            'attach': detailUrl + '/attach-from',
            'detach': detailUrl + '/detach-from'
        }

    class Meta:
        model = File
        fields = (
            'id',
            'name',
            'description',
            'document',
            'tags',
            'links',
        )


class FileSerializer(BasicFileSerializer):

    tags = TagListSerializerField()

    context = FileContextSerializer(many=True, read_only=True)

    class Meta:
        model = File
        fields = (
            'id',
            'name',
            'description',
            'created_by',
            'date_created',
            'date_updated',
            'document',
            'context',
            'tags',
            'links',
        )


class FilesMixInSerializer(object):

    files = serializers.SerializerMethodField()

    def get_files(self, obj):
        request = self.context.get('request')
        serializer = BasicFileSerializer(obj.files.all(), many=True, context={'request': request})
        return serializer.data


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
