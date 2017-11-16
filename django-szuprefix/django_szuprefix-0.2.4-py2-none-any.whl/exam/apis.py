# -*- coding:utf-8 -*-
from rest_framework.decorators import list_route
from rest_framework.serializers import ModelSerializer

from django_szuprefix.api.mixins import UserApiMixin
from django_szuprefix.saas.mixins import PartyMixin, PartySerializerMixin
from django_szuprefix.utils import modelutils
from .apps import Config

__author__ = 'denishuang'
from . import models
from rest_framework import serializers, viewsets
from django_szuprefix.api import register


class PaperSerializer(PartySerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Paper
        fields = ('title', 'content', 'content_object', 'is_active', 'create_time', 'id')




class PaperViewSet(PartyMixin, UserApiMixin, viewsets.ModelViewSet):
    queryset = models.Paper.objects.all()
    serializer_class = PaperSerializer


register(Config.label, 'paper', PaperViewSet)
