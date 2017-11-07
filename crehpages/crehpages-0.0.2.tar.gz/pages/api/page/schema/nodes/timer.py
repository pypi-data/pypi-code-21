# -*- coding: utf-8 -*-
import graphene
from graphene_django import DjangoObjectType

from pages.models.page import PageTimer
from pages.api.slider.schema.nodes.slider import SliderNode


class TimerNode(DjangoObjectType):

    class Meta:
        model = PageTimer
