# -*- encoding:utf-8 -*-
from braces.views import LoginRequiredMixin

from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.views.generic.list import BaseListView
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import DeletionMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.safestring import mark_safe
from django.contrib.auth.views import login as auth_login
from django.contrib.auth.views import logout as auth_logout
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django import forms

from .ajax import ajax_success


@login_required()
@permission_required(['auth:add_user'])
def sidebar_collapsed(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Bad request')
    col = request.POST.get('sidebar_collapsed', 'false')
    request.session['sidebar_collapsed'] = col
    return ajax_success({})


class MultipleDeleteView(
    LoginRequiredMixin,
    DeletionMixin,
    TemplateResponseMixin,
    BaseListView):
    http_method_names = ['post', 'get']
    allow_empty = False
    object_list_kwarg = 'obj'
    object_list_filter_key = 'pk'

    def get_context_data(self, **kwargs):
        form_fields = [forms.HiddenInput().render(
            self.object_list_kwarg,
            getattr(obj, self.object_list_filter_key, ''))
                       for obj in self.get_queryset()]
        kwargs['deletion_form'] = mark_safe('\n'.join(form_fields))
        return super(MultipleDeleteView, self).get_context_data(**kwargs)

    def get_queryset(self):
        queryset = super(MultipleDeleteView, self).get_queryset()
        if self.request.method == 'POST':
            object_ids = self.request.POST.getlist(self.object_list_kwarg)
        elif self.request.method == 'GET':
            object_ids = self.request.GET.getlist(self.object_list_kwarg)
        else:
            raise HttpResponseBadRequest
        filter_kwargs = {self.object_list_filter_key + '__in': object_ids}
        return queryset.filter(**filter_kwargs)

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.queryset = self.get_queryset()
        self.object = self.queryset
        success_url = self.get_success_url()
        self.queryset.delete()
        return HttpResponseRedirect(success_url)


def login(request):
    if request.user.is_authenticated():
        return redirect('index')
    return auth_login(request, template_name='bgframework/login.html')


def logout(request):
    return auth_logout(request, next_page=reverse('logout_after'))


def logout_after(request):
    return render(request, 'bgframework/logout.html', {})
