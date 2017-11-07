# -*- coding: utf-8 -*-
import graphene

from graphene import AbstractType

from pages.models.slider import Slider
from pages.api.slider.schema.nodes.slider import SliderNode


class SliderQuery(AbstractType):
    slider = graphene.Field(SliderNode, id=graphene.Int(), slug=graphene.String())
    sliders = graphene.List(SliderNode, description='List of sliders')

    def resolve_sliders(self, args, context, inf):
        return Slider.objects.activated()

    def resolve_slider(self, args, context, inf):
        page = Slider.objects.none()
        if args.get('id', None):
            return Slider.objects.activated().get(id=args.get('id', None))
        elif args.get('slug', None):
            page = Slider.objects.activated().get(slug=args.get('slug', None))
        return page
