#!/usr/bin/python
# -*- coding: utf-8 -*-

from . import bd_common

from .. import country

class BDCountry(country.ECountry, bd_common.BDCommon):

    @classmethod
    @bd_common.handle_error
    def list(cls, *args, **kwargs):
        api = cls._get_api_g()
        countries = api.list_countries(*args, **kwargs)
        countries = BDCountry.wrap(countries)
        return countries

    @classmethod
    def get_c(cls, country_code):
        countries = cls.list(limit = 0)
        for country in countries:
            is_same = country.country_code == country_code
            if not is_same: continue
            return country
        return None
