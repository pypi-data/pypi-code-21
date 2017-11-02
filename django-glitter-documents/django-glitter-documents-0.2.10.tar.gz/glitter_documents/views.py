# -*- coding: utf-8 -*-
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import DetailView, ListView

from glitter.mixins import GlitterDetailMixin

from .mixins import DocumentMixin
from .models import Category, Document


class DocumentListView(DocumentMixin, ListView):
    paginate_by = 10
    queryset = Document.objects.published()

    def get_queryset(self):
        queryset = super(DocumentListView, self).get_queryset()
        now = timezone.now()
        return queryset.filter(publish_at__lte=now)


class DocumentDetailView(DocumentMixin, GlitterDetailMixin, DetailView):

    def get_context_data(self, **kwargs):
        context = super(DocumentDetailView, self).get_context_data(**kwargs)
        context['current_category'] = self.object.category
        return context


class CategoryDocumentListView(DocumentMixin, ListView):
    template_name_suffix = '_category_list'
    paginate_by = 10
    queryset = Document.objects.published()

    def get_queryset(self):
        qs = super(CategoryDocumentListView, self).get_queryset()
        now = timezone.now()
        qs = qs.filter(publish_at__lte=now)

        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])

        query = Q(pk=self.category.pk) | Q(parent_category=self.category)
        categories = Category.objects.filter(query)

        return qs.filter(category__in=categories)

    def get_context_data(self, **kwargs):
        context = super(CategoryDocumentListView, self).get_context_data(**kwargs)
        context['current_category'] = self.category
        return context
