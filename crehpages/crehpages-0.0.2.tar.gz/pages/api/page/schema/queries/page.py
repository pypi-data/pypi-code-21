# -*- coding: utf-8 -*-
import graphene

from graphene import AbstractType

from pages.models.page import Page
from pages.api.page.schema.nodes.page import PageNode


class PageQuery(AbstractType):
    page = graphene.Field(PageNode, id=graphene.Int(), slug=graphene.String())
    pages = graphene.List(PageNode, description='List of pages')

    def resolve_pages(self, args, context, inf):
        return Page.objects.activated()

    def resolve_page(self, args, context, inf):
        page = Page.objects.none()
        if args.get('id', None):
            return Page.objects.activated().get(id=args.get('id', None))
        elif args.get('slug', None):
            page = Page.objects.activated().get(slug=args.get('slug', None))
        return page
