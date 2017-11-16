from django.core.urlresolvers import reverse
from django.shortcuts import resolve_url
from django.views.generic.edit import ModelFormMixin

from common_config.mixins import ImageFormMixin, AttachmentFormMixin
from . import models
# Create your views here.
from django.views.generic import CreateView, TemplateView, UpdateView, DetailView
from django.http import JsonResponse

class AttachmentUploadView(CreateView):
    model = models.Attachment
    fields = ("file",)

    def form_valid(self, form):
        self.object = r = form.save(False)
        r.owner = self.request.user
        r.name = r.file.name
        r.save()
        return JsonResponse({"error_code": 0, "file": {"id": r.id, "name": r.name, "url": r.file.url}})

    def form_invalid(self, form):
        return JsonResponse({"error_code": -1,"errors":form.errors})

class ImageUploadView(CreateView):
    model = models.Image
    fields = ("file",)

    def form_valid(self, form):
        self.object = r = form.save(False)
        r.owner = self.request.user
        r.save()
        from sorl.thumbnail import get_thumbnail
        thumb = get_thumbnail(self.object.file,self.request.GET.get("thumb","100x100"))
        return JsonResponse({"error_code": 0, "file": {"id": r.id, "url": r.file.url, "thumb_url":thumb.url }})

    def form_invalid(self, form):
        return JsonResponse({"error_code": -1,"errors":form.errors})


class ExcelTaskDetailView(DetailView):
    model = models.ExcelTask

    def get_queryset(self):
        return super(ExcelTaskDetailView, self).get_queryset().filter(owner=self.request.user)