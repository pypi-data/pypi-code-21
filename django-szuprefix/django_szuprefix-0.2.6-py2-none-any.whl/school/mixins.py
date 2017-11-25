# -*- coding:utf-8 -*-
from django.core.exceptions import PermissionDenied

from django_szuprefix.saas.mixins import PartyMixin, PartySerializerMixin

__author__ = 'denishuang'


class SchoolMixin(PartyMixin):
    def get_user_contexts(self, request, *args, **kwargs):
        ctx = super(SchoolMixin, self).get_user_contexts(request, *args, **kwargs)
        if not hasattr(self.party, "as_school"):
            raise PermissionDenied(u"当前网站用户不属于任何学校.")
        self.school = self.party.as_school
        return ctx + ["school"]

    def perform_create(self, serializer):
        serializer.save(school=self.school)


class SchoolSerializerMixin(PartySerializerMixin):
    pass
