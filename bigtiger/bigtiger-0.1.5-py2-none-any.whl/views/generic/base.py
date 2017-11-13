# -*- coding: utf-8 -*-

'''
Created on 2017-6-22
@author: linkeddt.com
'''

from __future__ import unicode_literals, print_function

from django.conf import settings
from django.http import Http404
from django.views.generic.base import ContextMixin


class SysConfContextMixin(ContextMixin):
    """读取配置文件中的系统全局配置到context中"""

    def get_context_data(self, **kwargs):
        if 'sysconf' not in kwargs:
            kwargs['sysconf'] = settings.SYS_CONFIG
        return super(SysConfContextMixin, self).get_context_data(**kwargs)


class PkContextMixin(object):
    pk_url_kwarg = 'pk'
    pk_split_kwarg = ','

    def get_pks(self):
        pk = self.get_pk()
        if pk is None:
            raise Http404()
        return pk.split(self.pk_split_kwarg)

    def get_pk(self):
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        return pk


class PermissionMixin(object):
    ref_url_kwarg = 'ref'

    def get_url_permission(self, url=None):
        if url is None:
            url = self.request.GET.get(
                self.ref_url_kwarg, None) or self.request.path

        ps = self.get_session_permissions()
        ps = [item for item in ps if item['menu_url'] == url]
        return None if len(ps) == 0 else ps[0]

    def get_session_permissions(self):
        return self.request.session.get(settings.PERMISSIONS_SESSION_KEY, None)
