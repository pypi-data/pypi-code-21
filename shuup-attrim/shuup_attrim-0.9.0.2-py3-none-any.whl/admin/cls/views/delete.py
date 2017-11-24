from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.generic import DetailView

from shuup.admin.utils.urls import get_model_url

from attrim.models import Class


class ClassDeleteView(DetailView):
    model = Class
    context_object_name = 'cls'

    def get(self, request, *args, **kwargs) -> HttpResponseRedirect:
        cls = self.get_object()
        cls_edit_url = get_model_url(cls)
        return HttpResponseRedirect(cls_edit_url)

    # noinspection PyUnusedLocal
    def post(self, request, *args, **kwargs) -> HttpResponseRedirect:
        cls = self.get_object()
        cls.delete()

        messages.success(request, _('%s has been marked deleted.') % cls)

        cls_list_url = reverse('shuup_admin:attrim.list')
        return HttpResponseRedirect(cls_list_url)
