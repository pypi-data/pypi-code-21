import graphene

from graphene_django.debug import DjangoDebug

from pages.api.page.schema.queries.page import PageQuery
from pages.api.slider.schema.queries.slider import SliderQuery


class Query(PageQuery, SliderQuery, graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name='__debug')

schema = graphene.Schema(query=Query, auto_camelcase=False)