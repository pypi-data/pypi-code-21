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

import copy

import six

from ._meta_models import Entity, Metric
from .._constants import display_series_threshold, display_series_part
from .._jsonutil import deserialize, serialize
from .._time_utilities import timediff_in_minutes, to_milliseconds, to_date, to_iso
from .._utilities import NoneDict


# ------------------------------------------------------------------------------
class Sample(object):
    """
    Class that represents a numeric value observed at some time with an optional annotation and versioning fields.
    If multiple samples have the same timestamp and are inserted for the same series, the latest sample prevails, unless the metric is optionally enabled for version tracking.
    """

    def __init__(self, value, x=None, time=None, version=None):
        self._v = copy.deepcopy(value) if not value == "Nan" else float("nan")
        self._x = x
        #:class:`datetime` object | `long` milliseconds | `str`  ISO 8601 date
        self._t = int(round(time.time() * 1000)) if time is None else to_milliseconds(time)
        self._d = to_date(self._t)
        # `.dict` version object including 'source' and 'status' keys
        self._version = version

    def _to_dict(self):
        d = {'v': self._v, 't': self._t}
        if self._x:
            d['x'] = self._x
        if self.version:
            d['version'] = self._version
        return d

    def __repr__(self):
        return "<Sample v={v}, t={t}, version={vv}>".format(v=self._v, t=self._t, vv=self._version)

    @property
    def v(self):
        return self._v

    @property
    def x(self):
        return self._x

    @property
    def t(self):
        return self._t

    def get_date(self):
        return self._d

    @property
    def version(self):
        return self._version

    @v.setter
    def v(self, v):
        self._v = v

    @x.setter
    def x(self, x):
        self._x = x

    @t.setter
    def t(self, t):
        self._t = to_milliseconds(t)
        self._d = to_date(self._t)

    @version.setter
    def version(self, value):
        self._version = value

    def _compare(self, other):
        return self._t - other.t

    def __lt__(self, other):
        return self._compare(other) < 0

    def __gt__(self, other):
        return self._compare(other) > 0

    def __eq__(self, other):
        return self._compare(other) == 0 and self.v == other.v

    def __le__(self, other):
        return self._compare(other) <= 0

    def __ge__(self, other):
        return self._compare(other) >= 0

    def __ne__(self, other):
        return self._compare(other) != 0


# ------------------------------------------------------------------------------
class Series(object):
    """
    Class representing a time series.
    Series is a time-indexed array of samples (observations), each consisting of a timestamp and a numeric value, for example CPU utilization or temperature.
    Each series is uniquely identified by metric name, entity name, and optional series tags.
    """

    def __init__(self, entity, metric, data=None, tags=None, last_insert_date=None, meta=None):
        #: `str` entity name
        self._entity = entity
        #: `str` metric name
        self._metric = metric
        #: `dict` of ``tag_name: tag_value`` pairs
        self._tags = NoneDict(tags)
        # `list` of :class:`.Sample` objects| `list` of {'t': time, 'v': value} objects
        self._data = []
        if data is not None:
            for data_unit in data:
                if isinstance(data_unit, dict):  # Compatibility
                    self._data.append(Sample(
                        value=data_unit['v'],
                        time=data_unit.get('t', data_unit.get('d', None)),
                        version=data_unit.get('version', None)
                    )
                    )
                else:
                    self._data.append(data_unit)
        # : `datetime` object | `long` milliseconds | `str` ISO 8601 date. Last time a value was received for this
        # metric by any series
        self._lastInsertDate = to_date(last_insert_date)
        #: `dict` of entity and metric objects
        if meta is None:
            self._meta = None
        else:
            self._meta = {}
            for k, v in six.iteritems(meta):
                if k == 'entity':
                    self._meta[k] = deserialize(v, Entity)
                elif k == 'metric':
                    self._meta[k] = deserialize(v, Metric)
                else:
                    self._meta[k] = v

    def __eq__(self, o):
        return self._entity == o.entity and self._metric == o.metric and self._tags == o.tags and self._data == o.data

    def __repr__(self):
        if len(self._data) > display_series_threshold:
            displayed_data = self._data[:display_series_part] + self._data[-display_series_part:]
        else:
            displayed_data = self._data
        rows = []
        versioned = False
        for sample in sorted(displayed_data):
            date = sample.get_date()
            value = sample.v
            row = '{0}{1: >14}'.format(date, value)
            if sample.version is not None:
                versioned = True
                source = sample.version.get('source', '-')
                status = sample.version.get('status', '-')
                row += '{0: >17}{1: >17}'.format(source, status)
            rows.append(row)
        if versioned:
            header = ('            date'
                      '                  value'
                      '   version_source'
                      '   version_status'
                      )
            rows.insert(0, header)
        if len(self._data) > 20:
            result = '\n'.join(rows[:-display_series_part]) + '\n...\n' + '\n'.join(rows[-display_series_part:])
        else:
            result = '\n'.join(rows)
        for key, value in six.iteritems(vars(type(self))):
            if isinstance(value, property) and key != 'data':
                attr = getattr(self, key)
                if attr is not None:
                    result += '\n{0}: {1}'.format(key, attr)
        return result

    def to_dictionary(self):
        return serialize(self)

    @staticmethod
    def from_dict(s):
        return deserialize(s, Series)

    def add_samples(self, *samples):
        """
        Add all given samples to the series
        """
        self._data.extend(samples)

    def sort(self, key=None, reverse=False):
        """
        Sort series samples in place
        :param key:
        :param reverse:
        """
        self._data.sort(key=key, reverse=reverse)

    def values(self):
        """
        Valid numeric samples in this series
        :return: list of `Number`
        """
        data = sorted(self._data)
        result = []
        for num, sample in enumerate(data):
            if num > 0 and sample.t == data[num - 1].t:
                result.pop()
            result.append(sample.v)
        return result

    def times(self):
        """
        Valid timestamps in this series
        :return: list of `str`
        """
        data = sorted(self._data)
        result = []
        for num, sample in enumerate(data):
            if num > 0 and sample.get_date() == data[num - 1].get_date():
                result.pop()
            new_time = to_iso(sample.get_date())
            result.append(new_time)
        return result

    @staticmethod
    def from_pandas_series(entity, metric, ts):
        """
        :param entity: `str` entity name
        :param metric: `str` metric name
        :param ts: pandas time series object
        :return: :class:`.Series` with data from pandas time series
        """
        res = Series(entity, metric)
        for dt in ts.index:
            res.data.append(Sample(value=ts[dt], time=dt))
        return res

    def to_pandas_series(self):
        """
        :return: pandas time series object
        """
        import pandas as pd
        return pd.Series(self.values(), index=self.times())

    def plot(self):
        """
        Plot series in matplotlib.pyplot
        """
        try:
            return self.to_pandas_series().plot()
        except ImportError:
            import matplotlib.pyplot as plt
            return plt.plot(self.times(), self.values())

    @property
    def entity(self):
        return self._entity

    @property
    def metric(self):
        return self._metric

    @property
    def tags(self):
        return self._tags

    @property
    def data(self):
        return self._data

    @property
    def meta(self):
        return self._meta

    @entity.setter
    def entity(self, value):
        self._entity = value

    @metric.setter
    def metric(self, value):
        self._metric = value

    @tags.setter
    def tags(self, value):
        self._tags = NoneDict(value)

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def last_insert_date(self):
        return self._lastInsertDate

    @last_insert_date.setter
    def last_insert_date(self, value):
        self._lastInsertDate = to_date(value)

    def get_elapsed_minutes(self):
        """Return elapsed time in minutes between current time and last insert date for the current series.

        :return: Time in minutes
        """
        return timediff_in_minutes(self.last_insert_date)

    def get_first_value(self):
        return self._data[0].v

    def get_last_value(self):
        return self._data[-1].v

    def get_first_value_date(self):
        return self._data[0].get_date()

    def get_last_value_date(self):
        return self._data[-1].get_date()


# ------------------------------------------------------------------------------
class Property(object):
    """
    Class representing a property record which contains keys and tags of string type.
    Properties represent metadata describing entities, such as device model, OS version, and location. 
    Each properties record is uniquely identified by entity name, property type and optional property keys.
    The property values are are stored as text and only last value is stored for the given primary key.
    """

    def __init__(self, type, entity, tags=None, key=None, date=None, meta=None):
        #: `str` property type name
        self._type = type
        #: `str` entity name
        self._entity = entity
        #: `dict` of ``name: value`` pairs that are not part of the key and contain descriptive information about the property record.
        self._tags = NoneDict(tags)
        #: `dict` of ``name: value`` pairs that uniquely identify the property record
        self._key = NoneDict(key)
        #: :class:`datetime` object | `long` milliseconds | `str`  ISO 8601 date, for example 2016-05-25T00:15:00Z. Set to server time at server side if omitted.
        self._date = to_date(date)
        #: `dict` of entity and metric objects
        if meta is not None:
            self._meta = {'entity': deserialize(meta['entity'], Entity)}

    def __repr__(self):
        return "<PROPERTY type={type}, entity={entity}, tags={tags}...>".format(type=self._type, entity=self._entity,
                                                                                tags=self._tags)

    @property
    def type(self):
        return self._type

    @property
    def entity(self):
        return self._entity

    @property
    def tags(self):
        return self._tags

    @property
    def key(self):
        return self._key

    @property
    def date(self):
        return self._date

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def meta(self):
        return self._meta

    @entity.setter
    def entity(self, value):
        self._entity = value

    @tags.setter
    def tags(self, value):
        self._tags = NoneDict(value)

    @key.setter
    def key(self, value):
        self._key = value

    @date.setter
    def date(self, value):
        self._date = to_date(value)


# ------------------------------------------------------------------------------
class Alert(object):
    """
    Class representing an open alert record.
    Alert is an event produced by the rule engine by applying pre-defined rules to incoming data.
    An alert is created when an expression specified in the rule evaluates to True. The alert is closed and deleted when the expression returns False.
    """

    def __init__(self, id, rule=None, entity=None, metric=None, last_event_date=None, open_date=None, value=None,
                 message=None, tags=None, text_value=None, severity=None, repeat_count=None, acknowledged=None,
                 open_value=None):
        self._id = id
        #: `str` rule
        self._rule = rule
        #: `str` entity
        self._entity = entity
        #: `str` metric
        self._metric = metric
        #: `str` | :class:`datetime` | `long` milliseconds when the last record was received
        self._lastEventDate = to_date(last_event_date)
        #: `str` | :class:`datetime` | `long` milliseconds when the alert was open
        self._openDate = to_date(open_date)
        #: `Number` last numeric value received
        self._value = value
        #: `str` text value
        self._message = message
        #: `dict`
        self._tags = NoneDict(tags)
        #: `str` text value
        self._textValue = text_value
        #: :class:`.Severity`
        self._severity = severity
        #: `int` number of times when the expression evaluated to true sequentially
        self._repeatCount = repeat_count
        #: `bool` acknowledgement status
        self._acknowledged = acknowledged
        #: `Number` first numeric value received.
        self._openValue = open_value

    def __repr__(self):
        return "<ALERT id={id}, text={text}, entity={entity}, metric={metric}, open_date={openDate}...>".format(
            id=self._id, entity=self._entity, metric=self._metric, openDate=self._openDate, text=self._textValue)

    @property
    def id(self):
        return self._id

    @property
    def entity(self):
        return self._entity

    @property
    def metric(self):
        return self._metric

    @property
    def open_date(self):
        return self._openDate

    @property
    def text_value(self):
        return self._textValue

    @property
    def rule(self):
        return self._rule

    @property
    def last_event_date(self):
        return self._lastEventDate

    @property
    def value(self):
        return self._value

    @property
    def message(self):
        return self._message

    @property
    def tags(self):
        return self._tags

    @property
    def severity(self):
        return self._severity

    @property
    def repeat_count(self):
        return self._repeatCount

    @property
    def acknowledged(self):
        return self._acknowledged

    @property
    def open_value(self):
        return self._openValue

    @id.setter
    def id(self, value):
        self._id = value

    @entity.setter
    def entity(self, value):
        self._entity = value

    @metric.setter
    def metric(self, value):
        self._metric = value

    @open_date.setter
    def open_date(self, value):
        self._openDate = to_date(value)

    @text_value.setter
    def text_value(self, value):
        self._textValue = value

    @rule.setter
    def rule(self, value):
        self._rule = value

    @last_event_date.setter
    def last_event_date(self, value):
        self._lastEventDate = to_date(value)

    @value.setter
    def value(self, value):
        self._value = value

    @message.setter
    def message(self, value):
        self._message = value

    @tags.setter
    def tags(self, value):
        self._tags = NoneDict(value)

    @severity.setter
    def severity(self, value):
        self._severity = value

    @repeat_count.setter
    def repeat_count(self, value):
        self._repeatCount = value

    @acknowledged.setter
    def acknowledged(self, value):
        self._acknowledged = value

    @open_value.setter
    def open_value(self, value):
        self._openValue = value


# ------------------------------------------------------------------------------
class AlertHistory(object):
    """
    Class representing history of an alert, including such values as alert duration, alert open date, repeat count, etc.
    """

    def __init__(self, alert=None, alert_duration=None, alert_open_date=None, entity=None, metric=None,
                 received_date=None,
                 repeat_count=None, rule=None, rule_expression=None, rule_filter=None, severity=None, tags=None,
                 type=None,
                 date=None, value=None, window=None):
        self._alert = alert
        #: `Number` time in milliseconds when alert was in OPEN or REPEAT state
        self._alertDuration = alert_duration
        #: `str` | :class:`datetime` | `long`
        self._alertOpenDate = to_date(alert_open_date)
        #: `str`
        self._entity = entity
        #: `str`
        self._metric = metric
        #: `str` | :class:`datetime` | `long`
        self._receivedDate = to_date(received_date)
        #: `int`
        self._repeatCount = repeat_count
        #: `str`
        self._rule = rule
        #: `str`
        self._ruleExpression = rule_expression
        #: `str`
        self._ruleFilter = rule_filter
        #: :class:`.Severity`
        self._severity = severity
        #: `str`
        self._tags = NoneDict(tags)
        #: `str` alert state when closed: OPEN, CANCEL, REPEAT
        self._type = type
        #: :class:`datetime` object | `long` milliseconds | `str` ISO 8601 date
        self._date = to_date(date)
        #: `Number` last numeric value received
        self._value = value
        #: `int` window length
        self._window = window

    def __repr__(self):
        return "<ALERT_HISTORY alert={alert}, metric={metric}, entity={entity}, date={date}, alert_open_date={alertOpenDate}...>".format(
            alert=self._alert, entity=self._entity, metric=self._metric, alertOpenDate=self._alertOpenDate,
            date=self._date)

    @property
    def alert(self):
        return self._alert

    @property
    def entity(self):
        return self._entity

    @property
    def metric(self):
        return self._metric

    @property
    def alert_open_date(self):
        return self._alertOpenDate

    @property
    def date(self):
        return self._date

    @property
    def alert_duration(self):
        return self._alertDuration

    @property
    def received_date(self):
        return self._receivedDate

    @property
    def repeat_count(self):
        return self._repeatCount

    @property
    def rule(self):
        return self._rule

    @property
    def rule_expression(self):
        return self._ruleExpression

    @property
    def rule_filter(self):
        return self._ruleFilter

    @property
    def schedule(self):
        return self._schedule

    @property
    def severity(self):
        return self._severity

    @property
    def tags(self):
        return self._tags

    @property
    def type(self):
        return self._type

    @property
    def value(self):
        return self._value

    @property
    def window(self):
        return self._window

    @alert.setter
    def alert(self, value):
        self._alert = value

    @entity.setter
    def entity(self, value):
        self._entity = value

    @metric.setter
    def metric(self, value):
        self._metric = value

    @alert_open_date.setter
    def alert_open_date(self, value):
        self._alertOpenDate = to_date(value)

    @date.setter
    def date(self, value):
        self._date = to_date(value)

    @alert_duration.setter
    def alert_duration(self, value):
        self._alertDuration = value

    @received_date.setter
    def received_date(self, value):
        self._receivedDate = to_date(value)

    @repeat_count.setter
    def repeat_count(self, value):
        self._repeatCount = value

    @rule.setter
    def rule(self, value):
        self._rule = value

    @rule_expression.setter
    def rule_expression(self, value):
        self._ruleExpression = value

    @rule_filter.setter
    def rule_filter(self, value):
        self._ruleFilter = value

    @schedule.setter
    def schedule(self, value):
        self._schedule = value

    @severity.setter
    def severity(self, value):
        self._severity = value

    @tags.setter
    def tags(self, value):
        self._tags = NoneDict(value)

    @type.setter
    def type(self, value):
        self._type = value

    @value.setter
    def value(self, value):
        self._value = value

    @window.setter
    def window(self, value):
        self._window = value


# ------------------------------------------------------------------------------
class Message(object):
    """
    Class representing a Message.
    Messages are events collected from system logs and messaging systems.
    Each message is related to an entity, has a set of tags and a free-form text message.
    Messages for the same entity, time and type/source tags are automatically de-duplicated.
    """

    def __init__(self, type, source, entity, date, severity, tags, message, persist=True):
        #: `str` message type
        self._type = type
        #: `str` message source
        self._source = source
        #: `str` entity name
        self._entity = entity
        #:`datetime` | `long` milliseconds | `str` ISO 8601 date when the message record was created
        self._date = to_date(date)
        #: :class:`.Severity`
        self._severity = severity
        #: `str` message tags
        self._tags = NoneDict(tags)
        #: `str`
        self._message = message
        #: `bool`
        self._persist = persist

    def __repr__(self):
        return "<MESSAGE type={t}, source={s}, entity={e}, message={m}, date={d}...>".format(t=self._type,
                                                                                             s=self._source,
                                                                                             e=self._entity,
                                                                                             m=self._message,
                                                                                             d=self._date)

    # Getters and setters
    @property
    def type(self):
        return self._type

    @property
    def entity(self):
        return self._entity

    @property
    def source(self):
        return self._source

    @property
    def date(self):
        return self._date

    @property
    def severity(self):
        return self._severity

    @property
    def tags(self):
        return self._tags

    @property
    def message(self):
        return self._message

    @property
    def persist(self):
        return self._persist

    @type.setter
    def type(self, value):
        self._type = value

    @entity.setter
    def entity(self, value):
        self._entity = value

    @source.setter
    def source(self, value):
        self._source = value

    @date.setter
    def date(self, value):
        self._date = to_date(value)

    @severity.setter
    def severity(self, value):
        self._severity = value

    @tags.setter
    def tags(self, value):
        self._tags = NoneDict(value)

    @message.setter
    def message(self, value):
        self._message = value

    @persist.setter
    def persist(self, value):
        self._persist = value
