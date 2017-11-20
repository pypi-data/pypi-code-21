# -*- coding: utf-8 -*-
import geoip2.database


def json_exporter(_ip_geo):
    return {
        'ip_address': _ip_geo.ip_address,
        'location_label': _ip_geo.location_label(),
        'postal_code': _ip_geo.postal_code(),
    }


class ProxyGeo(object):
    __db_reader = None

    def __init__(self, ip_address, locale='en'):
        if ProxyGeo.__db_reader is None:
            raise Exception('You should load geo ip city mmdb at first !')
        self._ip_address = ip_address
        self._locale = locale
        self.info = ProxyGeo.read(ip_address)

    @property
    def ip_address(self):
        return self._ip_address

    @property
    def locale(self):
        return self._locale

    @property
    def country(self):
        return self.info['country']

    @property
    def country_name(self):
        if self._locale is None:
            return self.info['country'].name
        return self.info['country'].names[self._locale]

    @property
    def city(self):
        return self.info['city']

    @property
    def city_name(self):
        if self._locale is None:
            return self.info['city'].name
        return self.info['city'].names[self._locale]

    @property
    def location(self):
        return self.info['location']

    @property
    def postal(self):
        return self.info['postal']

    def location_label(self, tmpl='{country}, {city}'):
        return tmpl.format(country=self.country_name, city=self.city_name)

    @property
    def timezone(self):
        return self.info['location'].timezone

    def position(self, tmpl='({latitude}, {longitude})'):
        return tmpl.format(latitude=self.info['location'].latitude, longitude=self.info['location'].longitude)

    def postal_code(self, most=True):
        postal_code = self.info['postal'].code
        if most is True:
            return postal_code
        code_confidence = self.info['postal'].confidence
        if code_confidence is None or code_confidence > 66:
            desc = 'must be {code}'.format(code=postal_code)
        elif 33 < code_confidence <= 66:
            desc = 'probably {code}'.format(code=postal_code)
        else:
            desc = 'probably {code}'.format(code=postal_code)
        return {
            'desc': desc,
            'code': postal_code
        }

    @property
    def zip_code(self):
        return self.postal_code()

    def __unicode__(self):
        return self.ip_address + '\'s geo info'

    def export(self, exporter=json_exporter):
        return exporter(self)

    @classmethod
    def export(cls, ip_address, exporter=json_exporter):
        return exporter(cls(ip_address=ip_address))

    @classmethod
    def read(cls, ip_address):
        response = cls.__db_reader.city(ip_address)
        return {
            'country': response.country,
            'city': response.city,
            'location': response.location,
            'postal': response.postal,
        }

    @classmethod
    def open_reader(cls, db_path):
        if cls.__db_reader is None:
            cls.__db_reader = geoip2.database.Reader(db_path)
        return cls

    @classmethod
    def close(cls):
        if cls.__db_reader is not None:
            cls.__db_reader.close()
