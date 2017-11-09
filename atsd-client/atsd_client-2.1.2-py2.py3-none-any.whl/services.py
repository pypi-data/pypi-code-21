# -*- coding: utf-8 -*-

"""
Copyright 2017 Axibase Corporation or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License").
You may not use this file except in compliance with the License.
A copy of the License is located at

https://www.axibase.com/atsd/axibase-apache-2.0.pdf

or in the "license" file accompanying this file. This file is distributed
on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
express or implied. See the License for the specific language governing
permissions and limitations under the License.
"""

from . import _jsonutil
from ._client import Client
from ._constants import *
from ._time_utilities import to_iso
from .exceptions import DataParseException, SQLException, ServerException
from .models import Series, Property, Alert, AlertHistory, Metric, Entity, EntityGroup, Message

try:
    from urllib import quote
    from StringIO import StringIO
    from urllib import urlencode
except ImportError:
    from urllib.parse import quote
    from io import StringIO
    from urllib.parse import urlencode

import six


def _check_name(name):
    if not isinstance(name, (six.binary_type, six.text_type)):
        raise TypeError('name should be str')
    if len(name) == 0:
        raise ValueError('name is empty')


class _Service(object):
    def __init__(self, conn):
        if not isinstance(conn, Client):
            raise ValueError('conn should be Client instance')
        self.conn = conn


# ------------------------------------------------------------------------ SERIES
class SeriesService(_Service):
    def insert(self, *series_objects):
        """Insert an array of samples for a given series identified by metric, entity, and series tags

        :param series_objects: :class:`.Series` objects
        :return: True if success
        """
        for series in series_objects:
            if len(series.data) == 0:
                raise DataParseException('data', Series, 'Inserting empty series')
        self.conn.post(series_insert_url, series_objects)
        return True

    def query(self, *queries):
        """Retrieve series for each query

        :param queries: :class:`.SeriesQuery` objects
        :return: list of :class:`.Series` objects
        """
        response = self.conn.post(series_query_url, queries)
        return [_jsonutil.deserialize(element, Series) for element in response]

    def url_query(self, *queries):
        """
        Unimplemented
        """
        raise NotImplementedError

    def csv_insert(self, *csvs):
        """
        Unimplemented
        """
        raise NotImplementedError


# -------------------------------------------------------------------- PROPERTIES
class PropertiesService(_Service):
    def insert(self, *properties):
        """Insert given properties

        :param properties: :class:`.Property`
        :return: True if success
        """
        self.conn.post(properties_insert_url, properties)
        return True

    def query(self, *queries):
        """Retrieves property records for each query

        :param queries: :class:`.PropertiesQuery`
        :return: list of :class:`.Property` objects
        """
        resp = self.conn.post(properties_query_url, queries)
        return _jsonutil.deserialize(resp, Property)

    def type_query(self, entity):
        """Returns an array of property types for the entity.

        :param entity: :class:`.Entity`
        :return: returns `list` of property types for the entity.
        """
        response = self.conn.get(properties_types_url.format(entity=quote(encode_if_required(entity.name), '')))
        return response

    def url_query(self, *queries):
        """
        Unimplemented
        """
        raise NotImplementedError

    def delete(self, *filters):
        """Delete properties for each query

        :param filters: :class:`.PropertyDeleteFilter`
        :return: True if success
        """
        response = self.conn.post(properties_delete_url, filters)
        return True


# ------------------------------------------------------------------------ ALERTS
class AlertsService(_Service):
    def query(self, *queries):
        """Retrieve alert records for each query

        :param queries: :class:`.AlertsQuery`
        :return: get of :class:`.Alert` objects
        """
        resp = self.conn.post(alerts_query_url, queries)
        return _jsonutil.deserialize(resp, Alert)

    def update(self, *updates):
        """Change acknowledgement status for the specified open alerts.

        :param updates: `dict`
        :return: True if success
        """
        response = self.conn.post(alerts_update_url, updates)
        return True

    def history_query(self, *queries):
        """Retrieve alert history for each query

        :param queries: :class:`.AlertHistoryQuery`
        :return: get of :class:`.AlertHistory` objects
        """
        resp = self.conn.post(alerts_history_url, queries)
        return _jsonutil.deserialize(resp, AlertHistory)

    def delete(self, *ids):
        """Delete alerts by id

        :param ids: `int`
        :return: True if success
        """
        response = self.conn.post(alerts_delete_url, ids)
        return True


# ---------------------------------------------------------------------- MESSAGES
class MessageService(_Service):
    def insert(self, *messages):
        """Insert specified messages

        :param messages: :class:`.Message`
        :return: True if success
        """
        resp = self.conn.post(messages_insert_url, messages)
        return True

    def query(self, *queries):
        """Retrieve messages for each query

        :param queries: :class:`.MessageQuery`
        :return: `list` of :class:`.Message` objects
        """
        resp = self.conn.post(messages_query_url, queries)
        return _jsonutil.deserialize(resp, Message)

    def statistics(self, *params):
        """
        Unimplemented
        """
        raise NotImplementedError


# ===============================================================================
#################################  META   #####################################
# ===============================================================================

# ----------------------------------------------------------------------- METRICS
class MetricsService(_Service):
    def get(self, name):
        """Retrieve metric.

        :param name: `str` metric name
        :return: :class:`.Metric`
        """
        _check_name(name)
        try:
            response = self.conn.get(metric_get_url.format(metric=quote(encode_if_required(name), '')))
        except ServerException as e:
            if e.status_code == 404:
                return None
            else:
                raise e
        return _jsonutil.deserialize(response, Metric)

    def list(self, expression=None, min_insert_date=None, max_insert_date=None, tags=None, limit=None):
        """Retrieve a `list` of metrics matching the specified filters.

        :param expression: `str`
        :param min_insert_date: `int` | `str` | None | :class:`datetime`
        :param max_insert_date: `int` | `str` | None | :class:`datetime`
        :param tags: `str`
        :param limit: `int`
        :return: :class:`.Metric` objects
        """
        params = {}
        if expression is not None:
            params['expression'] = expression
        if min_insert_date is not None:
            params['minInsertDate'] = to_iso(min_insert_date)
        if max_insert_date is not None:
            params['maxInsertDate'] = to_iso(max_insert_date)
        if tags is not None:
            params['tags'] = tags
        if limit is not None:
            params['limit'] = limit
        response = self.conn.get(metric_list_url, params)
        return _jsonutil.deserialize(response, Metric)

    def update(self, metric):
        """Update the specified metric.

        :param metric: :class:`.Metric`
        :return: True if success
        """
        self.conn.patch(metric_update_url.format(metric=quote(encode_if_required(metric.name), '')), metric)
        return True

    def create_or_replace(self, metric):
        """Create a metric or replace an existing metric.

        :param metric: :class:`.Metric`
        :return: True if success
        """
        self.conn.put(metric_create_or_replace_url.format(metric=quote(encode_if_required(metric.name), '')), metric)
        return True

    def delete(self, metric_name):
        """Delete the specified metric.

        :param metric_name: :class:`.Metric`
        :return: True if success
        """
        self.conn.delete(metric_delete_url.format(metric=quote(encode_if_required(metric_name), '')))
        return True

    def series(self, metric, entity=None, tags=None, min_insert_date=None, max_insert_date=None):
        """Retrieve series for the specified metric.

        :param metric: `str` | :class:`.Metric`
        :param entity: `str` | :class:`.Entity`
        :param tags: `dict`
        :param min_insert_date: `int` | `str` | None | :class:`datetime`
        :param max_insert_date: `int` | `str` | None | :class:`datetime`

        :return: :class:`.Series`
        """
        metric_name = metric.name if isinstance(metric, Metric) else metric
        _check_name(metric_name)

        params = {}
        if entity is not None:
            params['entity'] = entity.name if isinstance(entity, Entity) else entity
        if tags is not None and isinstance(tags, dict):
            for k, v in six.iteritems(tags):
                params['tags.%s' % k] = v
        if min_insert_date is not None:
            params['minInsertDate'] = to_iso(min_insert_date)
        if max_insert_date is not None:
            params['maxInsertDate'] = to_iso(max_insert_date)

        try:
            response = self.conn.get(metric_series_url.format(metric=quote(encode_if_required(metric_name), '')), params)
        except ServerException as e:
            if e.status_code == 404:
                return []
            else:
                raise e
        return _jsonutil.deserialize(response, Series)


# ------------------------------------------------------------------------------ ENTITIES
class EntitiesService(_Service):
    def get(self, entity_name):
        """Retrieve the entity

        :param entity_name: `str` entity name
        :return: :class:`.Entity`
        """
        _check_name(entity_name)
        try:
            response = self.conn.get(ent_get_url.format(entity=quote(encode_if_required(entity_name), '')))
        except ServerException as e:
            if e.status_code == 404:
                return None
            else:
                raise e
        return _jsonutil.deserialize(response, Entity)

    def list(self, expression=None, min_insert_date=None, max_insert_date=None, tags=None, limit=None):
        """Retrieve a list of entities matching the specified filters.

        :param expression: `str`
        :param min_insert_date: `str` | `int` | :class:`datetime`
        :param max_insert_date: `str` | `int` | :class:`datetime`
        :param tags: `dict`
        :param limit: `int`
        :return: :class:`.Entity` objects
        """
        params = dict()
        if expression is not None:
            params["expression"] = expression
        if min_insert_date is not None:
            params["minInsertDate"] = to_iso(min_insert_date)
        if max_insert_date is not None:
            params["maxInsertDate"] = to_iso(max_insert_date)
        if tags is not None:
            params["tags"] = tags
        if limit is not None:
            params["limit"] = limit
        resp = self.conn.get(ent_list_url, params)
        return _jsonutil.deserialize(resp, Entity)

    def update(self, entity):
        """Update the specified entity.

        :param entity: :class:`.Entity`
        :return: True if success
        """
        self.conn.patch(ent_update_url.format(entity=quote(encode_if_required(entity.name), '')), entity)
        return True

    def create_or_replace(self, entity):
        """Create an entity or an existing entity.

        :param entity: :class:`.Entity`
        :return: True if success
        """
        self.conn.put(ent_create_or_replace_url.format(entity=quote(encode_if_required(entity.name), '')), entity)
        return True

    def delete(self, entity):
        """Delete the specified entity.

        :param entity: :class:`.Entity`
        :return: True if success
        """
        entity_name = entity.name if isinstance(entity, Entity) else entity
        self.conn.delete(ent_delete_url.format(entity=quote(encode_if_required(entity_name), '')))
        return True

    def metrics(self, entity, expression=None, min_insert_date=None, max_insert_date=None, use_entity_insert_time=False,
                limit=None, tags=None):
        """Retrieve a `list` of metrics matching the specified filters.

        :param entity: `str` | :class:`.Entity`
        :param expression: `str`
        :param min_insert_date: `int` | `str` | None | :class:`datetime`
        :param max_insert_date: `int` | `str` | None | :class:`datetime`
        :param use_entity_insert_time: `bool` If true, last_insert_date is calculated for the specified entity and metric
        :param limit: `int`
        :param tags: `str`
        :return: :class:`.Metric` objects
        """
        entity_name = entity.name if isinstance(entity, Entity) else entity
        _check_name(entity_name)
        params = {}
        if expression is not None:
            params['expression'] = expression
        if min_insert_date is not None:
            params['minInsertDate'] = to_iso(min_insert_date)
        if max_insert_date is not None:
            params['maxInsertDate'] = to_iso(max_insert_date)
        params['useEntityInsertTime'] = use_entity_insert_time
        if limit is not None:
            params['limit'] = limit
        if tags is not None:
            params['tags'] = tags
        response = self.conn.get(ent_metrics_url.format(entity=quote(encode_if_required(entity_name), '')), params)
        return _jsonutil.deserialize(response, Metric)


# ------------------------------------------------------------------------------ ENTITIY GROUPS
class EntityGroupsService(_Service):
    def get(self, group_name):
        """Retrieve the specified entity group.

        :param group_name: `str` entity group name
        :return: :class:`.EntityGroup`
        """
        _check_name(group_name)
        try:
            group_name = encode_if_required(group_name)
            resp = self.conn.get(eg_get_url.format(group=quote(group_name, '')))
        except ServerException as e:
            if e.status_code == 404:
                return None
            else:
                raise e
        return _jsonutil.deserialize(resp, EntityGroup)

    def list(self, expression=None, tags=None, limit=None):
        """Retrieve a list of entity groups.

        :param expression: `str`
        :param tags: `dict`
        :param limit: `int`
        :return: :class:`.EntityGroup` objects
        """
        params = dict()
        if expression is not None:
            params["expression"] = expression
        if tags is not None:
            params["tags"] = tags
        if limit is not None:
            params["limit"] = limit
        resp = self.conn.get(eg_list_url, params)
        return _jsonutil.deserialize(resp, EntityGroup)

    def update(self, group):
        """Update the specified entity group.
        Unlike the replace method, fields and tags that are not specified in the request are left unchanged.

        :param group: :class:`.EntityGroup`
        :return: True if success
        """
        self.conn.patch(eg_update_url.format(group=quote(encode_if_required(group.name), '')), group)
        return True

    def create_or_replace(self, group, expression=None, tags=None):
        """Create an entity group or replace an existing entity group.

        :param group: :class:`.EntityGroup`
        :param expression: `str` describe entities that match a filter expression consisting of fields and operators
        :param tags: `dict` Entity tags, as requested with the tags parameter.
        :return: True if success
        """
        data = dict()
        if expression is not None:
            data["expression"] = expression
        if tags is not None:
            data["tags"] = tags
        self.conn.put(eg_create_or_replace_url.format(group=quote(group.name, '')), data)
        return True

    def delete(self, group):
        """Delete the specified entity group.
        Member entities and their data is not affected by this operation.

        :param group: :class:`.EntityGroup`
        :return: True if success
        """
        self.conn.delete(eg_delete_url.format(group=quote(group.name, '')))
        return True

    def get_entities(self, group_name, expression=None, min_insert_date=None, max_insert_date=None, tags=None, limit=None):
        """Retrieve a list of entities that are members of the specified entity group and which match the specified expression filter.

        :param group_name: `str`
        :param expression: `str`
        :param min_insert_date: `str` | `int` | :class:`datetime`
        :param max_insert_date: `str` | `int` | :class:`datetime`
        :param tags: `dict`
        :param limit: `int`
        :return: `list` of :class:`.Entity` objects
        """
        _check_name(group_name)
        params = dict()
        if expression is not None:
            params["expression"] = expression
        if min_insert_date is not None:
            params["minInsertDate"] = to_iso(min_insert_date)
        if max_insert_date is not None:
            params["maxInsertDate"] = to_iso(max_insert_date)
        if tags is not None:
            params["tags"] = tags
        if limit is not None:
            params["limit"] = limit
        resp = self.conn.get(eg_get_entities_url.format(group=quote(encode_if_required(group_name), '')), params)
        return _jsonutil.deserialize(resp, Entity)

    def add_entities(self, group_name, entities, create_entities=None):
        """Add entities as members to the specified entity group.
        Changing members of expression-based groups is not supported.
        Note that changing members of expression-based groups is not supported.

        :param group_name: `str`
        :param entities: `list` of :class:`.Entity` objects | `list` of `str` entity names
        :param create_entities: `bool` flag indicating if new entities from the submitted list will be created if such entities don't exist
        :return: True if success
        """
        _check_name(group_name)
        data = []
        for e in entities:
            data.append(e.name if isinstance(e, Entity) else e)
        params = {"createEntities": True if create_entities is None else create_entities}
        response = self.conn.post(eg_add_entities_url.format(group=quote(encode_if_required(group_name), '')), data, params=params)
        return True

    def set_entities(self, group_name, entities, create_entities=None):
        """Set members of the entity group from the specified entity list.
        All existing members that are not included in the request will be removed from members.
        If the array in the request is empty, all entities are removed from the group and are replaced with an empty list.
        Note that changing members of expression-based groups is not supported.

        :param group_name: `str`
        :param entities: `list` of :class:`.Entity` objects | `list` of `str` entity names 
        :param create_entities: `bool` flag indicating if new entities from the submitted list will be created if such entities don't exist
        :return: True if success
        """
        _check_name(group_name)
        data = []
        for e in entities:
            data.append(e.name if isinstance(e, Entity) else e)
        params = {"createEntities": True if create_entities is None else create_entities}
        response = self.conn.post(eg_set_entities_url.format(group=quote(encode_if_required(group_name), '')), data, params=params)
        return True

    def delete_entities(self, group_name, entities):
        """Remove specified entities from members of the specified entity group.
        To delete all entities, submit an empty list [] using the set_entities method.
        Note that changing members of expression-based groups is not supported.

        :param group_name: `str`
        :param data: `list` of :class:`.Entity` objects | `list` of `str` entity names
        :return: True if success
        """
        _check_name(group_name)
        data = []
        for e in entities:
            data.append(e.name if isinstance(e, Entity) else e)

        response = self.conn.post(eg_delete_entities_url.format(group=quote(encode_if_required(group_name), '')), data=data)
        return True


# ------------------------------------------------------------------------ SQL
class SQLService(_Service):
    def query(self, sql_query):
        """Execute SQL query.

        :param sql_query: `str`
        :return: :class:`.DataFrame` object
        """
        import pandas as pd
        response = self.query_with_params(sql_query)
        return pd.read_csv(StringIO(response), sep=',')

    def query_with_params(self, sql_query, params=None):
        """Execute SQL query with api parameters.

        :param sql_query: `str`
        :param params: `dict`
        :return: Content of the response
        """
        if params is None:
            params = {'outputFormat': 'csv'}
        params['q'] = sql_query
        try:
            response_text = self.conn.post(sql_query_url, None, urlencode(params))
        except ServerException as e:
            if e.status_code == 404:
                return None
            else:
                raise SQLException(e.status_code, e.content, sql_query)
        return response_text

    def cancel_query(self, query_id):
        """Cancel the execution of the specified SQL query identified by query id.

        :param query_id: `str`
        :return: True if success
        """
        response = self.conn.get(sql_cancel_url, urlencode({'queryId': query_id}))
        return True


# ------------------------------------------------------------------------------ COMMANDS
class CommandsService(_Service):
    def send_commands(self, commands):
        """Send a command or a batch of commands in Network API syntax via /api/v1/command

        :param commands: `str` | `list`
        :return: True if success
        """
        if type(commands) is not list: commands = [commands]
        data = '\n'.join(commands)
        response = self.conn.post_plain_text(commands_url, data)
        return True


def encode_if_required(name):
    name = name.encode('utf-8') if isinstance(name, six.string_types) else name
    return name

