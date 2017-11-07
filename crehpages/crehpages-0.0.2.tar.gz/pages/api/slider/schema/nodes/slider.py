# -*- coding: utf-8 -*-
import graphene
import json

from graphene_django import DjangoObjectType
from graphene.types.json import JSONString

from pages.models.slider import Slider, SliderItem, \
    SliderContentType, SliderContent


class SliderContentNode(DjangoObjectType):

    config = JSONString()

    class Meta:
        model = SliderContent

    def resolve_config(self, args, context, info):
        return json.loads(self.config)


class SliderContentTypeNode(DjangoObjectType):

    class Meta:
        model = SliderContentType


class SliderItemNode(DjangoObjectType):

    contents = graphene.List(SliderContentNode)

    absolute_url_picture_pc = graphene.String()

    absolute_url_picture_tablet = graphene.String()

    absolute_url_picture_mobile = graphene.String()

    class Meta:
        model = SliderItem

    def resolve_contents(self, args, request, info):
        return self.slidercontent_set.all().order_by('order')

    def resolve_absolute_url_picture_pc(self, args, request, info):
        return self.absolute_url_picture_pc

    def resolve_absolute_url_picture_tablet(self, args, request, info):
        return self.absolute_url_picture_tablet

    def resolve_absolute_url_picture_mobile(self, args, request, info):
        return self.absolute_url_picture_mobile


class SliderNode(DjangoObjectType):

    items = graphene.List(SliderItemNode)

    class Meta:
        model = Slider

    def resolve_items(self, args, request, info):
        return self.slideritem_set.all().order_by('order')

