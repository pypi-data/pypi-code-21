# -*- coding: utf-8 -*-
import graphene
from graphene_django import DjangoObjectType

from pages.models.page import Page
from pages.models.page import PageTimer
from pages.api.page.schema.nodes.timer import TimerNode
from pages.api.slider.schema.nodes.slider import SliderNode


class PageNode(DjangoObjectType):

    sliders = graphene.List(SliderNode)
    timer = graphene.Field(TimerNode)

    class Meta:
        model = Page

    def resolve_sliders(self, args, request, info):
        return self.slidercontent_set.all()

    def resolve_timer(self, args, request, info):
        page_timer = None
        page_timers = PageTimer.objects.filter(identifier=self.timer_id)
        if page_timers.exists():
            page_timer = page_timers.first()
        return page_timer
