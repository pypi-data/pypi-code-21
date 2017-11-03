# -*- coding: utf-8 -*-

'''
Created on 2017-6-22
@author: linkeddt.com
'''

from __future__ import unicode_literals, print_function

import os
import uuid

from django.conf import settings
from django.http import Http404
from django.http.response import JsonResponse
from django.views.generic.base import TemplateResponseMixin, ContextMixin, View

from suds.client import WebFault

from bigtiger.forms.admins import form_admin
from bigtiger.forms.forms import ExcelImportForm, ExcelImportFormAdmin
from bigtiger.views.generic.base import PermissionMixin, PkContextMixin
from bigtiger.views.generic.detail import SingleObjectTemplateResponseMixin
from bigtiger.excels import XlrdMixin


class FormMixin(PermissionMixin, ContextMixin):
    form_class = None
    form_admin_class = None
    initial = {}
    prefix = None

    def get_initial(self):
        return self.initial.copy()

    def get_prefix(self):
        return self.prefix

    def get_form_class(self):
        return self.form_class

    def get_form_admin_class(self):
        return self.form_admin_class

    def get_form(self, form_class):
        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
            'r': self.request,
            'c': self.kwargs
        }

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_context_data(self, **kwargs):
        context = {}
        context.update(kwargs)
        context['permission'] = self.get_url_permission()
        return super(FormMixin, self).get_context_data(**context)

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        # return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        if settings.DEBUG:
            for k, v in form.errors.iteritems():
                print('%(field)s:%(error)s' % {'field': k, 'error': v})


class ProcessFormView(View):

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        self.adminform = form_admin.register(form, self.get_form_admin_class())
        context = self.get_context_data(adminform=self.adminform)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        result = {}
        if form.is_valid():
            result = self.form_valid(form)
        else:
            self.form_invalid(form)

        self.adminform = form_admin.register(form, self.get_form_admin_class())
        context = self.get_context_data(adminform=self.adminform, **result)
        return self.render_to_response(context)

    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)


class BaseFormView(FormMixin, ProcessFormView):
    """
    A base view for displaying a form
    """


class FormView(TemplateResponseMixin, BaseFormView):
    """
    A view for displaying a form, and rendering a template response.
    """


class BaseCreateView(FormMixin, ProcessFormView):

    def get(self, request, *args, **kwargs):
        return super(BaseCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(BaseCreateView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        result = {}
        try:
            self.add(form.cleaned_data)
        except WebFault as e:
            result['errorinfo'] = '操作失败，连接api失败，请重试。'
        except Exception as e:
            result['errorinfo'] = '操作失败，请重试。 '
        else:
            result['successinfo'] = '操作成功。'
        return result

    def form_invalid(self, form):
        return super(BaseCreateView, self).form_invalid(form)


class CreateView(SingleObjectTemplateResponseMixin, BaseCreateView):
    """
    View for creating a new object instance,
    with a response rendered by template.
    """


class BaseImportView(FormMixin, XlrdMixin, ProcessFormView):
    form_class = ExcelImportForm
    form_admin_class = ExcelImportFormAdmin
    sheet_index = 0
    start_line_number = 2

    def get_context_data(self, **kwargs):
        kwargs.update({'excel_template_name': self.excel_template_name})
        return FormMixin.get_context_data(self, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(BaseImportView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(BaseImportView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        context = {}
        try:
            import_dir = os.path.join(settings.MEDIA_ROOT, 'imports')
            if not os.path.exists(import_dir):
                os.makedirs(import_dir)

            f = form.files['excel_file_file']
            file_path = os.path.join(
                import_dir, '%s%s' % (uuid.uuid4(), f.name))

            with open(file_path, 'wb+') as f1:
                for chunk in f.chunks():
                    f1.write(chunk)

            data_lines, page_errors = self.read_xlsx(
                file_path, self.sheet_index, self.start_line_number)
            if page_errors:
                context['PAGE_ERRORS'] = page_errors
                raise ValueError('数据格式不正确，修改后重试')
            else:
                self.import_data(data_lines)
        except ValueError, e:
            context['errorinfo'] = u'数据格式不正确，修改后重试.'
        except Exception, e:
            context['errorinfo'] = u'操作失败，请重试。'
        else:
            context['successinfo'] = u'操作成功。'

        return context

    def form_invalid(self, form):
        return super(BaseImportView, self).form_invalid(form)


class ImportView(SingleObjectTemplateResponseMixin, BaseImportView):
    """
    View for creating a new object instance,
    with a response rendered by template.
    """
    template_name = 'admin/baseimport.htm'


class BaseUpdateView(FormMixin, PkContextMixin, ProcessFormView):

    def get(self, request, *args, **kwargs):
        pk = self.get_pk()
        if pk is None:
            raise Http404()

        self.initial = self.get_init_form_data(pk)
        return super(BaseUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(BaseUpdateView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        result = {}
        try:
            self.modify(form.cleaned_data)
        except WebFault, e:
            result['errorinfo'] = u'操作失败，连接api失败，请重试。', e
        except Exception, e:
            result['errorinfo'] = u'操作失败，请重试。', e
        else:
            result['successinfo'] = u'操作成功。'
        return result

    def form_invalid(self, form):
        return super(BaseUpdateView, self).form_invalid(form)


class UpdateView(SingleObjectTemplateResponseMixin, BaseUpdateView):
    """
    View for updating an object,
    with a response rendered by template.
    """


class MimeTypeContextMixin(object):
    mime_type_kwarg = 'MIME_TYPE'

    def get_mime_type(self):
        return self.kwargs.get(self.mime_type_kwarg, None)


class MimeTypeGetView(PkContextMixin, MimeTypeContextMixin, ContextMixin, View):

    def get(self, request, *args, **kwargs):
        pks = self.get_pks()
        mime_type = self.get_mime_type()

        try:
            handler = getattr(self, mime_type, None)
            if handler:
                return handler(pks)
            else:
                raise Http404()
        except WebFault as e:
            msg = u'操作失败，连接api失败，请重试。'
        except Exception, e:
            msg = u'操作失败，请重试。'
        return JsonResponse({'success': False, 'message': msg})


class MimeTypePostView(PkContextMixin, MimeTypeContextMixin, ContextMixin, View):

    def post(self, request, *args, **kwargs):
        pks = self.get_pks()
        mime_type = self.get_mime_type()

        try:
            handler = getattr(self, mime_type, None)
            if handler:
                msg = handler(pks)
            else:
                raise Http404()
            if not msg:
                return JsonResponse({'success': True, 'message': '操作成功'})
        except WebFault as e:
            msg = u'操作失败，连接api失败，请重试。'
        except Exception, e:
            msg = u'操作失败，请重试。'
        return JsonResponse({'success': False, 'message': msg})


class BaseDeleteView(MimeTypePostView):

    def get_mime_type(self):
        return 'delete'


class DeleteView(BaseDeleteView):
    pass
