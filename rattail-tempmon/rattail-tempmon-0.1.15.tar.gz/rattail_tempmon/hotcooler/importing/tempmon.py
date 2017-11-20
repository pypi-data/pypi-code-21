# -*- coding: utf-8 -*-
"""
HotCooler -> Tempmon importers
"""

from __future__ import unicode_literals, absolute_import

import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import orm
import sqlsoup

from rattail import importing
from rattail.util import OrderedDict
from rattail.time import make_utc
from rattail_tempmon.db import Session as TempmonSession, model as tempmon


class FromTempmonToHotCooler(importing.FromSQLAlchemyHandler, importing.ToSQLAlchemyHandler):
    """
    Handler for Tempmon -> HotCooler data import
    """
    host_title = "Tempmon"
    local_title = "HotCooler"

    def make_host_session(self):
        return TempmonSession()

    def make_session(self):
        self.soup = sqlsoup.SQLSoup(self.config.hotcooler_engine)
        return self.soup.session

    def get_importers(self):
        importers = OrderedDict()
        importers['Client'] = ClientImporter
        importers['Probe'] = ProbeImporter
        importers['Reading'] = ReadingImporter
        return importers

    def get_importer_kwargs(self, key, **kwargs):
        kwargs = super(FromTempmonToHotCooler, self).get_importer_kwargs(key, **kwargs)
        kwargs['soup'] = self.soup
        return kwargs


class FromTempmon(importing.FromSQLAlchemy):
    """
    Base class for importers where Tempmon is host
    """

    def normalize_host_object(self, obj):
        data = dict([(field, getattr(obj, field, None)) for field in self.fields])
        data['uuid'] = str(UUID(data['uuid']))
        for field in self.fields:
            if isinstance(data[field], datetime.datetime):
                data[field] = make_utc(data[field], tzinfo=True)
        return data


class ToHotCooler(importing.ToSQLAlchemy):
    """
    Base class for importers where HotCooler is local/target
    """
    key = 'uuid'

    @property
    def model_mapper(self):
        soup_model = self.get_soup_model(self.soup)
        return orm.class_mapper(soup_model)

    def cache_local_data(self, host_data=None):
        soup_model = self.get_soup_model(self.soup)
        return self.cache_model(soup_model, key=self.get_cache_key,
                                query=self.cache_query(),
                                normalizer=self.normalize_cache_object)

    def cache_query(self):
        soup_model = self.get_soup_model(self.soup)
        return self.session.query(soup_model)

    def normalize_local_object(self, obj):
        data = super(ToHotCooler, self).normalize_local_object(obj)
        for field in self.fields:
            if isinstance(data[field], datetime.datetime):
                data[field] = make_utc(data[field], tzinfo=True)
        return data

    def make_object(self):
        soup_model = self.get_soup_model(self.soup)
        return soup_model()

    def create_object(self, key, host_data):
        # TODO: this seems hacky..?
        return super(importing.ToSQLAlchemy, self).create_object(key, host_data)


class ClientImporter(FromTempmon, ToHotCooler):
    """
    Tempmon -> HotCooler importer for Client data
    """
    host_model_class = tempmon.Client
    supported_fields = [
        'uuid',
        'config_key',
        'hostname',
        'location',
        'delay',
        'enabled',
        'online',
    ]

    def get_soup_model(self, soup):
        return soup.client


class ProbeImporter(FromTempmon, ToHotCooler):
    """
    Tempmon -> HotCooler importer for Probe data
    """
    host_model_class = tempmon.Probe
    supported_fields = [
        'uuid',
        'client_id',
        'config_key',
        'appliance_type',
        'description',
        'device_path',
        'enabled',
        'good_temp_min',
        'good_temp_max',
        'critical_temp_min',
        'critical_temp_max',
        'therm_status_timeout',
        'status_alert_timeout',
    ]

    def get_soup_model(self, soup):
        return soup.probe

    def setup(self):
        self.clients = self.cache_model(self.soup.client, key='uuid')

    def normalize_host_object(self, probe):
        data = super(ProbeImporter, self).normalize_host_object(probe)
        uuid = str(UUID(probe.client_uuid))
        client = self.clients.get(uuid)
        data['client_id'] = client.id
        return data


class ReadingImporter(FromTempmon, ToHotCooler):
    """
    Tempmon -> HotCooler importer for Reading data
    """
    host_model_class = tempmon.Reading
    supported_fields = [
        'uuid',
        'client_id',
        'probe_id',
        'taken',
        'degrees_f',
    ]

    def get_soup_model(self, soup):
        return soup.reading

    def setup(self):
        self.clients = self.cache_model(self.soup.client, key='uuid')
        self.probes = self.cache_model(self.soup.probe, key='uuid')

    def normalize_host_object(self, reading):
        data = super(ReadingImporter, self).normalize_host_object(reading)
        uuid = str(UUID(reading.client_uuid))
        client = self.clients.get(uuid)
        data['client_id'] = client.id
        uuid = str(UUID(reading.probe_uuid))
        probe = self.probes.get(uuid)
        data['probe_id'] = probe.id
        return data
