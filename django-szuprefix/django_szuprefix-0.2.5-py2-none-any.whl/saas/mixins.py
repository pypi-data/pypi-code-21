# -*- coding:utf-8 -*-
from django.core.exceptions import PermissionDenied
from django.forms import ModelChoiceField
from rest_framework.relations import RelatedField

from django_szuprefix.api.mixins import RestCreateMixin

__author__ = 'denishuang'


class PartyMixin(RestCreateMixin):
    def get_user_contexts(self, request, *args, **kwargs):
        if not hasattr(request.user, "as_saas_worker"):
            raise PermissionDenied(u"当前网站用户不属于任何团体组织.")
        self.worker = request.user.as_saas_worker
        self.party = self.worker.party
        return ["worker", "party"]

    def dispatch(self, request, *args, **kwargs):
        self._extra_context_data = self.get_user_contexts(request, *args, **kwargs)
        return super(PartyMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(PartyMixin, self).get_context_data(**kwargs)
        for f in self._extra_context_data:
            ctx[f] = getattr(self, f)
        return ctx

    def get_queryset(self):
        return super(PartyMixin, self).get_queryset().filter(party=self.party)

    def get_form_kwargs(self):
        r = super(PartyMixin, self).get_form_kwargs()
        r['party'] = self.party
        return r

    def get_serializer(self, *args, **kwargs):
        kwargs['party'] = self.party
        return super(PartyMixin, self).get_serializer(*args, **kwargs)


class SubdomainSerializerMixin(object):
    subdomain_fields = []

    def __init__(self, *args, **kwargs):
        for f in self.subdomain_fields:
            if f in kwargs:
                setattr(self, f, kwargs.pop(f))
        super(SubdomainSerializerMixin, self).__init__(*args, **kwargs)
        self.addFilter2RelativeFields()

    def addFilter2RelativeFields(self):
        if not self.subdomain_fields:
            return
        for n, f in self.fields.iteritems():
            model = f.queryset.model
            if isinstance(f, (RelatedField, ModelChoiceField)):
                d = dict([(sf, getattr(self, sf)) for sf in self.subdomain_fields if hasattr(model, sf)])
                if d:
                    f.queryset = f.queryset.filter(**d)


class PartyFormMixin(object):
    party = None

    def __init__(self, *args, **kwargs):
        if 'party' in kwargs:
            self.party = kwargs.pop('party')
        super(PartyFormMixin, self).__init__(*args, **kwargs)
        self.addFilter2ModelChoiceFields()

    def addFilter2ModelChoiceFields(self):
        for n, f in self.fields.iteritems():
            if isinstance(f, ModelChoiceField) and f.queryset and hasattr(f.queryset.model, 'party'):
                f.queryset = f.queryset.filter(party=self.party)

    def save(self, commit=True):
        self.instance.party = self.party
        return super(PartyFormMixin, self).save(commit)



class PartySerializerMixin(object):
    party = None

    def __init__(self, *args, **kwargs):
        if 'party' in kwargs:
            self.party = kwargs.pop('party')
        super(PartySerializerMixin, self).__init__(*args, **kwargs)
        self.addFilter2RelativeFields()

    def addFilter2RelativeFields(self):
        for n, f in self.fields.iteritems():
            if isinstance(f, RelatedField) and f.queryset and hasattr(f.queryset.model, 'party'):
                f.queryset = f.queryset.filter(party=self.party)

    def save(self, **kwargs):
        kwargs["party"] = self.party
        return super(PartySerializerMixin, self).save(**kwargs)

class UserSerializerMixin(object):
    user = None

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(UserSerializerMixin, self).__init__(*args, **kwargs)
        self.addFilter2RelativeFields()

    def addFilter2RelativeFields(self):
        for n, f in self.fields.iteritems():
            if isinstance(f, RelatedField) and hasattr(f.queryset.model, 'user'):
                f.queryset = f.queryset.filter(user=self.user)
