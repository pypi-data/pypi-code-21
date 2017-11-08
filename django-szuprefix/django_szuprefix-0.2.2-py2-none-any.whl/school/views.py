from django_tables2 import SingleTableView

from ..utils.views  import FormResponseJsonMixin, ContextJsonDumpsMixin, TableResponseJsonMixin, \
    SearchFormMixin, SearchFormResponseJsonMixin
from . import models
# Create your views here.
from django.views.generic import CreateView, TemplateView, UpdateView, DetailView
from django.http import JsonResponse


class SchoolCreateView(FormResponseJsonMixin, ContextJsonDumpsMixin, CreateView):
    model = models.School
    fields = ('name', 'type')


class StudentDetailView(ContextJsonDumpsMixin, DetailView):
    model = models.Student


class StudentListView(ContextJsonDumpsMixin, SingleTableView):
    model = models.Student
