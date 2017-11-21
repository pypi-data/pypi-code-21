#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import calendar
import datetime

import appier

class EBase(appier.LocalModel):

    id = dict(
        type = int
    )

    id_str = dict()

    @classmethod
    def _build(cls, model, map):
        super(EBase, cls)._build(model, map)
        ident_name = cls._ident_name()
        ident = model.get(ident_name, None)
        model["id"] = model.get("id", -1)
        model["ident"] = ident
        model["ident_name"] = ident_name
        model[ident_name] = ident

    @classmethod
    def uncamelcase(cls, name):
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    @classmethod
    def string_from_timestamp(cls, timestamp, format = "%d/%m/%Y"):
        date = datetime.datetime.utcfromtimestamp(timestamp)
        date_string = date.strftime(format)
        return date_string

    @classmethod
    def timestamp_from_string(cls, date_string, format = "%d/%m/%Y"):
        date = datetime.datetime.strptime(date_string, format)
        date_utc = date.utctimetuple()
        timestamp = calendar.timegm(date_utc)
        return timestamp

    @classmethod
    def _get_adapter_g(cls):
        from .. import factory
        ref = factory.Factory.get_adapter_l()
        return ref

    @classmethod
    def _get_api_g(cls, *args, **kwargs):
        ref = cls._get_adapter_g()
        if not ref: return None
        return ref._get_api(*args, **kwargs)

    @classmethod
    def _ident_name(cls):
        return "id"

    @property
    def ident(self):
        return getattr(self, self.ident_name)

    @property
    def ident_name(self):
        cls = self.__class__
        return cls._ident_name()

    def _get_adapter(self, *args, **kwargs):
        cls = self.__class__
        if not self.ref: return cls._get_adapter_g()
        return self.ref

    def _get_api(self, *args, **kwargs):
        cls = self.__class__
        ref = self._get_adapter()
        if not ref: return None
        return ref._get_api(*args, **kwargs)
