from django.conf import settings
from django.contrib.admin.utils import quote
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import six
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View

from wagtail.wagtailadmin import messages
from wagtail.contrib.modeladmin.views import CreateView, EditView, DeleteView, IndexView

from wapps.errors import HttpResponseError

from .models import BaseForm


def render_response(request, template, ctx, status=200, **html_kwargs):
    if request.is_ajax():
        return JsonResponse(ctx, status=status)
    else:
        ctx.update(html_kwargs)
        return render(request, template, ctx)


class ProcessFormView(View):
    error_template = 'wapps/forms/error.html'
    success_template = 'wapps/forms/success.html'
    page_template = 'wapps/forms/page.html'

    def get_formdef_or_404(self, request, pk):
        try:
            return BaseForm.objects.get_subclass(id=pk)
        except BaseForm.DoesNotExist:
            ctx = {
                'message': six.text_type(settings.WAPPS_FORMS_ERROR_MSG), # NOQA
                'detail': 'Could not find Form with id {}'.format(pk)
            }
            response = render_response(request, self.error_template, ctx, status=400)
            raise HttpResponseError(response)

    def get(self, request, pk):
        formdef = self.get_formdef_or_404(request, pk)
        return render(request, self.page_template, formdef.add_to_context({}))

    def post(self, request, pk):
        formdef = self.get_formdef_or_404(request, pk)
        form = formdef.get_form(request.POST, request.FILES)

        if form.is_valid():
            formdef.process_form_submission(form)
        else:
            ctx = {
                'message': six.text_type(settings.WAPPS_FORMS_ERROR_MSG),
                'detail': form.errors
            }
            formdef.add_to_context(ctx)
            return render_response(request, self.page_template, ctx, status=400)

        ctx = {
            'message': formdef.success_message or six.text_type(settings.WAPPS_FORMS_SUCCESS_MSG)
        }

        formdef.add_to_context(ctx, form)

        return render_response(request, self.success_template, ctx)


class ModelFormMixin(object):
    def get_success_message_buttons(self, instance):
        button_url = self.url_helper.get_action_url('edit',
                                                    instance._meta.app_label,
                                                    instance._meta.model_name,
                                                    quote(instance.pk))
        return [messages.button(button_url, _('Edit'))]


class InstanceMixin(object):
    @cached_property
    def app_label(self):
        return self.instance._meta.app_label

    @cached_property
    def model_name(self):
        return self.instance._meta.model_name

    @cached_property
    def edit_url(self):
        return self.url_helper.get_action_url('edit',
                                              self.app_label,
                                              self.model_name,
                                              self.pk_quoted)

    @cached_property
    def delete_url(self):
        return self.url_helper.get_action_url('delete',
                                              self.app_label,
                                              self.model_name,
                                              self.pk_quoted)


class CreateAdminView(ModelFormMixin, CreateView):
    pass


class EditAdminView(ModelFormMixin, InstanceMixin, EditView):
    pass


class DeleteAdminView(InstanceMixin, DeleteView):
    pass


class SubmissionsView(IndexView):
    def get_buttons_for_obj(self, obj):
        return []
