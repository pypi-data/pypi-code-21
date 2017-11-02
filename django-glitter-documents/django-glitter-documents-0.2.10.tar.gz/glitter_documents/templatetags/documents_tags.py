# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template
from django.db.models import Q
from django.utils import timezone

from ..models import Category, Document

register = template.Library()


@register.assignment_tag
def get_latest_documents(count=5, category=None):
    """ Accepts category or category slug. """
    document_list = Document.objects.published()
    now = timezone.now()
    document_list = document_list.filter(publish_at__lte=now)

    # If object is given as a slug, fetch the actual object or set category
    # to None so it is not used for filtering.
    if category is not None:
        if not isinstance(category, Category):
            try:
                category = Category.objects.get(slug=category)
            except Category.DoesNotExist:
                category = None

    # Optional filter by category, can be either a sub or parent category
    if category:
        query = Q(pk=category.pk) | Q(parent_category=category)
        categories = Category.objects.filter(query)
        document_list = document_list.filter(category__in=categories)

    return document_list[:count]
