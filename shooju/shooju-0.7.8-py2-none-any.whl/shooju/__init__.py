import os
import tempfile
from collections import defaultdict, OrderedDict
from datetime import date
import datetime
import calendar
from operator import truth
import time
import sys
import warnings
from logging import getLogger
import json

import requests

if sys.version_info[0] >= 3:
    basestring = str


# global lib options
class Options(object):
    POINT_SERIALIZERS = ['shooju_point', 'milli_tuple']

    def __init__(self, sjts=False, sjts_chunk_size=16384, sjts_stream=True, point_serializer='shooju_point'):
        super(Options, self).__init__()
        self._point_serializer = None
        self.sjts = sjts  # does nothing for now
        self.sjts_chunk_size = sjts_chunk_size
        self.sjts_stream = sjts_stream
        self.point_serializer = point_serializer

    @property
    def point_serializer(self):
        return self._point_serializer

    @point_serializer.setter
    def point_serializer(self, val):
        assert val in self.POINT_SERIALIZERS, \
            '{} unknown point serializer. supported: {}'.format(val, ', '.join(self.POINT_SERIALIZERS))
        self._point_serializer = val


options = Options()

logger = getLogger('shooju_client')


try:
    import pandas
    import numpy

    PANDAS_SUPPORT = True

    import re

    KEY_RE = re.compile(r'\{([\w\d\.]+)}')

except ImportError:
    PANDAS_SUPPORT = False


class ConnectionError(Exception):
    """
    Connection Errors
    """
    pass


class ShoojuApiError(Exception):
    """
    Shooju API errors
    """

    def __init__(self, message=''):
        super(ShoojuApiError, self).__init__(message)
        self.message = message


def sid(*args):
    """
    Constructs a series id using the list of arguments

    :param args: parts of the series id
    :return: formatted series id
    :rtype: str
    """
    return "\\".join(args)


class Point(object):
    """
    Point represents a value in the remote API
    """

    def __init__(self, dt, value):
        """
        Representation of a point for a time series

        :param int datetime.datetime datetime.date dt: date for the point
        :param float value: value of the point
        """
        self.date = dt
        self.value = value

    @property
    def value(self):
        """
        Value of the point

        :return: value of the point
        :rtype: float
        """
        return self._val

    @value.setter
    def value(self, value):
        """
        Sets the value of the point, only accepts float

        :param float value: value of the point
        """
        if value is not None:
            value = float(value)  # testing if it's a float
        self._val = value

    @property
    def date(self):
        """
        Date of the point

        :return: date
        :rtype: datetime.date
        """
        return datetime.date(self._dt.year, self._dt.month, self._dt.day)

    @date.setter
    def date(self, value):
        """
        Sets the date of the point

        :param int float datetime.datetime datetime.date value:
        :raise ValueError:
        """
        if isinstance(value, (int, long, float)):
            self._dt = datetime.datetime.utcfromtimestamp(value / 1000)
        elif isinstance(value, datetime.datetime):
            self._dt = value
        elif isinstance(value, date):
            self._dt = datetime.datetime(value.year, value.month, value.day, 0, 0, 0, 0)
        else:
            raise ValueError("You can pass millis or datetime.date objects only")

    @property
    def datetime(self):
        """
        Date of the point as datetime.datetime

        :return: date of the point
        :rtype: datetime.datetime
        """
        return self._dt

    def to_dict(self):
        """
        Returns back a dictionary of the point
        which will be ready to be serialized in the
        next steps ...
        """
        return {
            datetime_to_milli(self._dt): self._val
        }

    def __repr__(self):
        return "Point(%s, %s)" % (self._dt, self.value)


def milli_to_datetime(milli):
    """
    Converts millis to utc datetime

    :param int float milli: time in milliseconds
    :return:
    """
    return datetime.datetime.utcfromtimestamp(milli / 1000)


def date_to_milli(dt):
    """
    Date to utc millis time

    :param datetime.date dt: date
    :return: the date as a milliseconds time string
    :rtype: str
    """
    dd = datetime.datetime(dt.year, dt.month, dt.day, 0, 0, 0, 0)
    return datetime_to_milli(dd)


def datetime_to_milli(dt):
    """
    Datetime to utc time in milliseconds

    :param datetime.datetime dt: date
    :return: the date as a milliseconds time string
    :rtype : str
    """
    return str(int(calendar.timegm(dt.utctimetuple())) * 1000)


def to_milli(dt):
    """
    Date to utc time in milliseconds

    :param datetime.date datetime.datetime dt: date to be converted
    :return: the date as a milliseconds time string
    :rtype: str
    """
    if isinstance(dt, datetime.datetime):
        return datetime_to_milli(dt)
    elif isinstance(dt, date):
        return date_to_milli(dt)
    else:
        raise ValueError("You can pass milliseconds or datetime.date objects only")


class Connection(object):
    """
    Represents a Connection to the Shooju api
    """

    def __init__(self, server, *args, **kwargs):
        """
        Initializes connection to the Shooju API.
        Must use either user+api_key or email+google_oauth_token to authenticate.

        :param str user: Shooju username
        :param api_key: Shooju API key
        :param google_oauth_token: Google API refresh token
        :param email: Google account email
        :param server: Shooju server with protocol (https://alpha2.shooju.com) or just account name (alpha2).
        :param retries: Number of attempts to execute api call
        :param retry_delay: Time between api call attempts (seconds)
        """
        self.shooju_api = ShoojuApi(server, *args, **kwargs)
        self.job_source = "python"

    @property
    def user(self):
        """
        Returns current user.
        """
        return self.shooju_api.client._user

    @property
    def raw(self):
        """
        Retrieves a REST client to perform arbitrary requests to the Shooju API.

        Usage:
            conn.raw.get('/teams/', params={'q': 'test'})
            conn.raw.post('/teams/myteam/', data_json={'description': 'description'})
            conn.raw.delete('/series/single/', params={'series_id': series_id}

        :return: shooju.Client instance
        """
        return self.shooju_api.client

    @property
    def pd(self):
        """
        If pandas is installed, pd can be used to format data as pandas data structures

        Usage::
            conn.pd.search_series('', size=0, query_size=3, fields=['code_country'])  #returns a pandas.DataFrame
            conn.pd.get_fields('series_id') #returns a pandas.Series
            conn.get_points('series_id', size=30) #returns a pandas.Series

        :return: shooju.PandasFormatter instance
        """
        if PANDAS_SUPPORT:
            if not hasattr(self, '_pandas_formatter'):
                self._pandas_formatter = PandasFormatter(self.shooju_api)
            return self._pandas_formatter
        else:
            return None

    def change_job_source(self, name):
        """
        Changes the name of the source

        :param str name: name of the new job source
        """
        self.job_source = name

    def search(self, query='', date_start=None, date_finish=None, fields=None, max_points=0, size=None,
               per_page=10, sort_on=None, sort_order=None, query_size=None):
        """
        Performs a block search against the Shooju API

        :param query: query to perform
        :param per_page: number of series to return
        :param query_size: number of series to return (deprecated)
        :param date_start: start date for points
        :param date_finish: end date for points
        :param fields: list of fields to retrieve
        :param max_points: number of points to retrieve per series
        :param size: number of points to retrieve per series (deprecated)
        :param sort_on: field used to sort the results
        :param sort_order: order of search results.
        :return: a dict hashed by series id with a list of Points per series id
        :rtype: dict
        """
        data = self.shooju_api.search_series(query, date_start, date_finish, max_points, per_page=per_page,
                                             fields=fields, size=size, sort_on=sort_on, sort_order=sort_order,
                                             query_size=query_size)
        return self._process_search_response(data)

    def scroll(self, query='', date_start=None, date_finish=None, fields=None, max_points=0, size=None,
               scroll_batch_size=2500, sort_on=None, sort_order=None, operators=None, query_size=None):
        """
        Performs a scroll search. Function is a generator, yields series

        Usage::

            for series in conn.scroll_series():
                # do something with the dict

        :param query: query to perform
        :param date_start: start date for points
        :param date_finish: end date for points
        :param fields: list of fields to retrieve
        :param sort_on: field used to sort the results
        :param sort_order: order of search results.
        :param max_points: number of points to retrieve per series
        :param size: number of points to retrieve per series (deprecated)
        :param query_size: number of series to pull per single scroll
        :param operators: array of series operators
        """
        if size is not None:
            max_points = size

        if query_size is not None:
            scroll_batch_size = query_size

        r = self.shooju_api.search_series(query, date_start, date_finish, max_points=max_points,
                                          fields=fields, scroll=True, scroll_batch_size=scroll_batch_size,
                                          sort_on=sort_on, sort_order=sort_order, operators=operators)
        scroll_id = r['scroll_id']
        series_left = r['total']

        while series_left > 0:
            for s in self._process_search_response(r):
                yield s
            series_left -= len(r['series'])
            if series_left:
                r = self.shooju_api.scroll_series(scroll_id)

    def get_points(self, series_id, date_start=None, date_finish=None, max_points=10,
                   snapshot_job_id=None, snapshot_date=None, size=None):
        """
        Retrieves points for a series id. Can select time range. If series does not exist it returns
        None

        :param str series_id: series id
        :param datetime.datetime date_start: get points < date
        :param datetime.datetime date_finish: get points > date
        :param int size: number of points to get
        :param int snapshot_job_id: job identifier. If not passed returns latest data, otherwise returns
                                    the historic snapshot of how the series looked after the job.
        :param datetime.datetime snapshot_date: If not passed returns latest data, otherwise returns
                                    the historic snapshot of how the series looked at that datetime.
        :param int max_points: number of points to get
        :param int size: number of points to get (this parameter is deprecated, use max_points)
        :return: a list of Points
        :rtype: list
        """
        if size is not None:
            max_points = size
        data = self.shooju_api.get_series(series_id, date_start, date_finish, max_points=max_points,
                                          snapshot_job_id=snapshot_job_id, snapshot_date=snapshot_date)
        if options.point_serializer == 'shooju_point':
            point = Point
        else:
            point = lambda dt, val: (dt, val)

        return list(map(lambda p: point(p[0], p[1]), data.get('points', []))) if data is not None else None

    def get_point(self, series_id, dt, snapshot_job_id=None, snapshot_date=None):
        """
        Retrieves a point from the series, if the series does not exist it returns None, if the point
        does not exist it returns a Point with value of None

        :param str series_id: series id
        :param datetime.datetime dt: date of the point
        :param int snapshot_job_id: job identifier. If not passed returns latest data, otherwise returns
                                    the historic snapshot of how the series looked after the job.
        :param datetime.datetime snapshot_date: If not passed returns latest data, otherwise returns
                                    the historic snapshot of how the series looked at that datetime.
        :return: a Point instance
        :rtype: shooju.Point
        """
        points = self.get_points(series_id, dt, dt, snapshot_job_id=snapshot_job_id, snapshot_date=snapshot_date)
        if points is None:
            return None
        return points[0] if len(points) == 1 else Point(dt, None)

    def get_field(self, series_id, field, snapshot_job_id=None, snapshot_date=None):
        """
        Retrieves a field value from the series. If the field does not exist or the series does not exist
        it returns None.

        :param str series_id: series id
        :param str field: name of the field
        :param int snapshot_job_id: job identifier. If not passed returns latest data, otherwise returns
                                    the historic snapshot of how the series looked after the job.
        :param datetime.datetime snapshot_date: If not passed returns latest data, otherwise returns
                                    the historic snapshot of how the series looked at that datetime.
        :return: value of the field
        :rtype: str
        """
        fields = self.get_fields(series_id, [field], snapshot_job_id=snapshot_job_id, snapshot_date=snapshot_date)
        if fields is None:
            return None
        return fields.get(field)

    def get_fields(self, series_id, fields='*', snapshot_job_id=None, snapshot_date=None,):
        """
        Retrieves fields from series. Parameter `fields` is a list of field names. If `fields` is not
        present, all of the fields are returned

        :param str series_id: series id
        :param list fields: list of fields to retrieve
        :param int snapshot_job_id: job identifier. If not passed returns latest data, otherwise returns
                                    the historic snapshot of how the series looked after the job.
        :param datetime.datetime snapshot_date: If not passed returns latest data, otherwise returns
                                    the historic snapshot of how the series looked at that datetime.
        :return: fields of the series
        :rtype: dict
        """
        data = self.shooju_api.get_series(series_id, size=0, fields=fields,
                                          snapshot_job_id=snapshot_job_id, snapshot_date=snapshot_date,)
        if data is None:
            return None
        return data.get('fields', {})

    def register_job(self, description, notes="", batch_size=1,
                     dry_run=False, reported_group=None, reported_at=None):
        """
        Registers a job in Shooju. A job is used to write series.

        :param str description: brief description
        :param str notes: notes about the job
        :param int batch_size: indicates the size of the buffer before creating new series in the server
        :param bool dry_run: if True data will no be send to Shooju. it just will be printed.
        :param str reported_group: if set, the job will be associated with the reported group specified
        :param datetime reported_at: required if reported_group is set
        :return: a RemoteJob instance
        :rtype: shooju.RemoteJob
        """
        if len(description) < 3:
            raise ValueError('description should be longer than 3 characters')

        if not dry_run:
            data = self.shooju_api.register_job(description, notes, self.job_source, reported_group, reported_at)
            return RemoteJob(
                self, data['job_id'], batch_size=batch_size, collision_retry_timeout=10.0)
        else:
            return DryRunJob(self, None, batch_size=batch_size, collision_retry_timeout=10.0)

    def create_uploader_session(self):
        """
        Registers an uploader session.

        Used for uploading files to Shooju.

        :return: a UploaderSession instance
        :rtype: shooju.UploaderSession
        """
        data = self.shooju_api.create_uploader_session()
        return UploaderSession(self, data['session_id'])

    def mget(self):
        """
        Creates a multiget object to perform requests in batch
        """
        return GetBulk(self)

    def delete(self, series_id, force=False):
        """
        If force parameter is False moves series to trash. Otherwise removes series.

        :param series_id: series id
        :param force: if True permanently deletes without moving to trash
        :return: True if the deletion was successful
        """
        warnings.warn('Connection.delete is deprecated. Use RemoteJob.delete instead.')
        return self.shooju_api.delete_series(series_id, force)

    def delete_by_query(self, query, force=False):
        """
        If force==True permanently deletes all series that match the query - be careful.
        Otherwise moves these series to trash.

        :param query: query to base the deletion on
        :param force: if True permanently deletes without moving to trash
        :return: number of series deleted (moved to trash)
        """
        warnings.warn('Connection.delete_by_query is deprecated. Use RemoteJob.delete_by_query instead.')
        return self.shooju_api.delete_series_by_query(query, force)

    def download_file(self, file_id, filename=None):
        """
        Downloads a file. If no `filename` is provided, a temporary file is created

        :param file_id: file id
        :param filename: file name for downloaded file
        :return: File instance
        """
        return self.shooju_api.download_file(file_id, filename)

    def _post_bulk(self, bulk_data, job_id=None, collision_retry_timeout=60, async=False):
        """
        Helper method to perform a series POST bulk request. Do not used directly

        :param list bulk_data: list of requests
        :param str int job_id: job id
        :param int collision_retry_timeout: delay before do next attempt if series was already lock to update
        :param bool async: use async bulk request
        :return: dict with the response
        """
        return self.shooju_api.bulk_series(self.shooju_api.API_SERIES_BULK_POST, bulk_data,
                                           job_id, collision_retry_timeout, async)

    def _get_bulk(self, bulk_data):
        """
        Internal method use get_bulk method to create
        GetBulk object and to to do getting bulk operations
        through it. @bulk_data is the dict to be sent to server
        """
        return self.shooju_api.bulk_series(self.shooju_api.API_SERIES, bulk_data)

    def _process_search_response(self, data):
        """
        Helper method to convert a api series search response to the module data structures
        :param data: api series response
        :return: array of series objects
        :rtype: list
        """
        results = list()
        for s in data['series']:
            s.setdefault('fields', {})
            if 'points' in s:
                s['points'] = [Point(d, v) for d, v in s['points']]
            results.append(s)
        return results


class PandasFormatter(object):

    NULL_VALUE = 'null'

    def __init__(self, api_client):
        """

        :param shooju.ShoojuApi api_client: ShoojuApi instance
        """
        self.api_client = api_client

    def search(self, query='', date_start=None, date_finish=None, size=10, fields=None, query_size=10, key_field=None):
        """
        Performs a block search and returns the results in pandas.DataFrame.

        :param query: query to perform
        :param query_size: number of series to return
        :param date_start: start date for points
        :param date_finish: end date for points
        :param size: number of points to retrieve per series
        :param fields: list of fields to retrieve
        :return: a pandas.DataFrame
        :rtype: pandas.DataFrame
        """
        if key_field:
            fields = self._get_fields_in_key(key_field)
        response = self.api_client.search_series(query, date_start, date_finish, size, query_size, fields)
        return self._process_search_request(response, key_field=key_field)

    def get_points(self, series_id, date_start=None, date_finish=None, size=10):
        """
        Gets the points of a series

        :param str series_id: series id
        :param datetime.datetime date_start: start date for points
        :param datetime.datetime date_finish: end date for points
        :param int size: number of points to retrieve
        :return: a pandas.Series with the points
        """
        response = self.api_client.get_series(series_id, date_start, date_finish, size, fields=[])
        index = [milli_to_datetime(p[0]) for p in response['points']]
        values = [p[1] for p in response['points']]
        return pandas.Series(values, index)

    def get_fields(self, series_id, fields=None):
        """
        Gets the fields for a series

        :param series_id: series id
        :param fields: list of fields
        :return: a pandas.Series with the fields
        """
        response = self.api_client.get_series(series_id, size=0, fields=fields)
        return pandas.Series(response['fields'])

    def _process_search_request(self, response, key_field=None):
        """
        Processes the search results and returns a pandas.DataFrame

        If there are only points it returns a DataFrame with columns for series_id and the dates of the points,
        if there are only fields it returns a DataFrame with colums for series_id and the name of the fields,
        if there are both it returns a DataFrame with columns for series_id, the name of the fields, date and points,
        the size of the DataFrame is number of series ids * number of dates in the result

        :param dict response: api response dict
        :return: a pandas.DataFrame with the search result data
        """
        series_ids = response['series_ids']
        if not series_ids:
            return pandas.DataFrame()

        if key_field:
            fields_for_key = response.pop('fields', {})

        has_fields = truth(response.get('fields', {}).get('fields'))
        has_points = truth(response['points'])

        if has_points and has_fields:
            series_dates = response['points']['dates']
            num_of_dates = len(series_dates)
            num_of_series = len(series_ids)

            # preparing dict to feed DataFrame
            data = {
                'series_id': list(flatten([series_id] * num_of_dates for series_id in series_ids)),
                'date':  list(map(milli_to_datetime, series_dates * num_of_series)),
                'points': list(roundrobin(*response['points']['values']))
            }
            data.update(
                    {field: list(flatten([value] * num_of_dates
                                         for value in response['fields']['values'][i]))
                     for i, field in enumerate(response['fields']['fields'])}
            )
        elif has_points:
            data = {}
            if key_field:
                fields_in_key = self._get_fields_in_key(key_field)
            for j, series_id in enumerate(series_ids):
                series = {}
                for i, dt in enumerate(response['points']['dates']):
                    if key_field:
                        key = self._get_column_name(key_field, fields_in_key, fields_for_key, j)
                    else:
                        key = series_id
                    value = response['points']['values'][i][j]
                    if value is None:
                        value = numpy.nan
                    series[milli_to_datetime(dt)] = value
                data[key] = series

        elif has_fields:
            data = {'series_id': series_ids}
            data.update(
                {field: response['fields']['values'][i] for i, field in enumerate(response['fields']['fields'])}
            )
        else:
            data = {'series_id': series_ids}

        return pandas.DataFrame(data)

    def _get_column_name(self, key_field, fields_in_key, fields, series_num):
        if not fields_in_key:  # no fields were requested, probably user error like {test
            return self.NULL_VALUE

        # one field case, no format, just return the value fo the field
        if '{' not in key_field:
            value = fields['values'][0][series_num]
            value = value if value is not None else self.NULL_VALUE
            return value

        field_dict = {}
        for i, field in enumerate(fields['fields']):
            value = fields['values'][i][series_num]
            value = value if value is not None else self.NULL_VALUE
            if '.' in field:
                field_sanitized = field.replace('.', '')
                key_field = key_field.replace(field, field_sanitized)
                field = field_sanitized
            field_dict[field] = value

        # fill fields that didn't might not be in the list of fields
        for field in fields_in_key:
            if field not in field_dict:
                field_dict[field] = self.NULL_VALUE

        return key_field.format(**field_dict)

    def _get_fields_in_key(self, key_field):
        if '{' in key_field:
            return KEY_RE.findall(key_field)
        else:
            return [key_field]


class ShoojuApi(object):
    """
    Class used to encapsulate Shooju API methods. Methods return the json decoded response from the server and raise
    an error if the response had errors.
    """

    API_SERIES = '/series'
    API_SERIES_SINGLE = '/series/single'
    API_SERIES_BULK_POST = '/series/bulk/'
    API_SERIES_DELETE = '/series/delete'
    API_JOBS = '/jobs/'
    API_FILES = '/files/{id}/download'
    API_STATUS = '/status/green'
    API_PING = '/status/ping'
    API_GOOGLE_OAUTH = '/auth/googleoauth'
    API_UPLOADER_SESSION = '/uploader/session'

    def __init__(self, server, *args, **kwargs):
        server = server if server.startswith('http') else 'https://{}.shooju.com'.format(server)
        if len(args) >= 2:
            user, api_key = args[:2]
        else:
            user, api_key = kwargs.get('user'), kwargs.get('api_key')
        
        if not all((user, api_key)):
            email = kwargs.get('email', os.environ.get('SHOOJU_EMAIL'))
            google_auth_token = kwargs.get('google_oauth_token', os.environ.get('SHOOJU_GOOGLE_OAUTH_TOKEN'))
            
            if email and google_auth_token:
                anonymous_client = Client(server)
                credentials = anonymous_client.post(self.API_GOOGLE_OAUTH,
                                                    data_json={'token': google_auth_token,
                                                               'email': email})
                user, api_key = credentials['user'], credentials['api_secret']

        if not all((user, api_key)):
            raise ShoojuApiError('Must use either user+api_key or email+google_oauth_token to authenticate.')

        self.client = Client(server, user, api_key,
                             retries=kwargs.get('retries'),
                             retry_delay=kwargs.get('retry_delay'))

    def get_series(self, series_id, date_start=None, date_finish=None,
                   max_points=None, fields=None, snapshot_job_id=None, snapshot_date=None, **kwargs):
        """
        Retrieves series

        :param str series_id: series id
        :param datetime.datetime date_start: start date for points
        :param datetime.datetime date_finish:  end date for points
        :param int max_points: number of points to retrieve
        :param list fields: list of fields to retrieve
        :param int snapshot_job_id: job identifier. If not passed returns latest data, otherwise returns
                                    the historic snapshot of how the series looked after the job.
        :param datetime.datetime snapshot_date: If not passed returns latest data, otherwise returns
                                    the historic snapshot of how the series looked at that datetime.
        :param datetime.datetime reported_date: If not passed returns latest data, otherwise returns
                                    the historic snapshot of how the series looked as of the reported date.
        :return: api response
        :rtype: dict
        """
        max_points = max_points or kwargs.get('size')
        params = {
            'date_format': 'milli',
            'df': to_milli(date_start) if date_start else 'MIN',
            'dt': to_milli(date_finish) if date_finish else 'MAX',
            'series_id': series_id,
            'snapshot_job_id': snapshot_job_id,
            'snapshot_date': to_milli(snapshot_date) if snapshot_date else None,
            'fields': '',
        }

        if fields is not None:
            params['fields'] = ','.join(fields)

        if max_points is not None:
            params['max_points'] = max_points

        return self.client.get(self.API_SERIES, params=params)['series'][0]

    def bulk_series(self, api, requests, job_id=None, collision_retry_timeout=60, async=False):
        """
        Executes a bulk series request

        :param str api: api path to call
        :param list requests: list of dict with the requests to be performed
        :param int str job_id: job id
        :param int collision_retry_timeout: delay before do next attempt if series was already lock to update
        :param bool async: call async bulk request
        :return: api response
        :rtype: dict
        """
        # this logic uses 2 api - old and new one which has some differences in requests and responses format
        if api == self.API_SERIES:
            request_key = response_key = 'series'
        else:
            request_key = 'requests'
            response_key = 'responses'

        # by this logic we trying to retry failed sub-requests and bring all responses together in to same order
        req_by_index = {i: r for i, r in enumerate(requests)}
        resp_by_index = {}
        params = {k: v for k, v in {'job_id': job_id, 'async': int(async), 'date_format': 'milli'}.items() if k}

        req_index_to_send = req_by_index.keys()
        attempts_left = 3

        while req_index_to_send and attempts_left:
            req_index_to_send = sorted(req_index_to_send)
            req_index_to_send_again = list()
            attempts_left -= 1

            requests_to_send = [req_by_index[r] for r in req_index_to_send]
            payload = {request_key: requests_to_send}
            response = self.client.post(api, ignore_exceptions=True, data_json=payload, params=params)
            if response_key not in response:  # looks like entire bulk request failed
                _check_errors(response)

            for i, resp in enumerate(response[response_key]):
                if not self._can_retry(resp) or not attempts_left:  # this is either success or final attempt
                    resp_by_index[req_index_to_send[i]] = resp
                else:
                    logger.debug(u'retrying bulk request because of: {error} {description}'.format(**resp))
                    req_index_to_send_again.append(req_index_to_send[i])  # we will try this again
            req_index_to_send = req_index_to_send_again
            if attempts_left and req_index_to_send:
                time.sleep(collision_retry_timeout)
        responses = [r[1] for r in sorted(resp_by_index.items(), key=lambda x: x[0])]
        _check_bulk_api_errors(responses)
        return responses

    @staticmethod
    def _can_retry(resp):
        """
        Returns True if error in response can be retried.
        """
        if resp.get('error') and 'series is locked for change' in resp.get('description', ''):
            return True
        else:
            return False

    def delete_series(self, series_id, force=False, job_id=None):
        """
        If force parameter is False moves series to trash. Otherwise removes series.

        :param series_id: series id
        :param force: if True permanently deletes without moving to trash
        :param job_id: job id to associate with deleted series
        :return: True if the deletion was successful
        """
        params = {'series_id': series_id}
        if force:
            params['force'] = force
        if job_id:
            params['job_id'] = job_id
        self.client.delete(self.API_SERIES_SINGLE, params=params)
        return True

    def delete_series_by_query(self, query, force=False, job_id=None):
        """
        Permanently deletes all series that match the query - be careful

        :param query: query to base the deletion on
        :param force: if True permanently deletes without moving to trash
        :param job_id: job id to associate with deleted series
        :return: number of series deleted
        """
        return self.client.delete(self.API_SERIES_DELETE,
                                  data_json={'query': query, 'force': force, 'job_id': job_id})['deleted']

    def create_uploader_session(self):
        """
        Registers uploader session.
        :return:
        """
        return self.client.post(self.API_UPLOADER_SESSION)

    def register_job(self, description, notes='', source='python', reported_group=None, reported_at=None):
        """
        Registers a job in Shooju.

        :param str description: brief description
        :param str notes: notes about the job
        :param str source: source of the job
        :return: api response
        :rtype: dict
        """
        payload = {
            "source": source,
            "description": description,
            "notes": notes
        }
        if reported_group:
            payload.update({
                'reported_group':reported_group,
                'reported_at':reported_at.isoformat()
            })

        data = self.client.post(self.API_JOBS, data_json=payload)
        return data

    def download_file(self, file_id, filename=None):
        """
        Downloads a file. If no `filename` is provided, a temporary file is created

        :param file_id: file id
        :param filename: file name for downloaded file
        :return: File instance
        """
        path = self.API_FILES.format(id=file_id)
        if filename:
            f = open(filename, 'w+b')
        else:
            f = tempfile.NamedTemporaryFile(prefix='download')

        r = self.client.get(path, binary_response=True)

        for chunk in r.iter_content(chunk_size=16 * 1024):
            if chunk:
                f.write(chunk)
                f.flush()
        f.seek(0, 0)
        return f

    def search_series(self, query='', date_start=None, date_finish=None, max_points=0,
                      scroll_batch_size=None, per_page=None, fields=None, scroll=False, sort_on=None,
                      sort_order='asc', operators=None, size=None, query_size=None):
        """
        Performs a search request to the shooju api

        :param query: query string
        :param date_start: points start date
        :param date_finish: points end date
        :param max_points: number of points
        :param size: number of  (deprecated parameter)
        :param scroll_batch_size: number of series to retrieve per scroll request
        :param per_page: number of series to retrieve per page
        :param query_size: number of series to retrieve (deprecated)
        :param fields: list of fields to retrieve
        :param scroll: flag indicating if it's a scroll search
        :param sort_on: field name to sort series on
        :param sort_order: sort direction
        :param scroll: flag indicating if it's a scroll search
        :param operators: array of series operators
        :return: dict with the api response
        """
        if size is not None:
            max_points = size

        params = {
            'query': query,
            'date_format': 'milli',
            'df': to_milli(date_start) if date_start else 'MIN',
            'dt': to_milli(date_finish) if date_finish else 'MAX',
            'max_points': max_points,
        }

        if fields:
            params['fields'] = ','.join(fields)

        if scroll_batch_size is not None:
            params['scroll_batch_size'] = scroll_batch_size

        if per_page:
            params['per_page'] = per_page

        if query_size:
            params.update({
                'scroll_batch_size': query_size,
                'per_page': query_size
            })

        if scroll:
            params['scroll'] = 'y'

        if sort_on:
            params['sort'] = '{} {}'.format(sort_on, sort_order)

        if operators:
            params['operators'] = '@{}'.format('@'.join(operators))

        return self.client.get(self.API_SERIES, params=params)

    def scroll_series(self, scroll_id):
        """
        Series scroll endpoint. Retrieves the next scroll data. Should be used in tandem with
        search_series with scroll flag set to True.

        Scroll has finished when no more series are returned

        :param scroll_id: scroll id
        :return: api response
        :rtype: dict
        """
        response = self.client.get(self.API_SERIES, params={'scroll_id': scroll_id})
        return response

    def api_status(self):
        """
        Checks Shooju API status

        :return: api response
        :rtype: dict
        """
        return self.client.get(self.API_STATUS)

    def ping(self):
        """
        Pings Shooju API

        :return: API response
        """
        return self.client.get(self.API_PING)


class Client(object):

    ALLOWED_METHODS = ('get', 'post', 'delete')  # list of allowed HTTP methods

    def __init__(self, host, user=None, password=None, base_path='/api/1', retries=None, retry_delay=None):
        """
        REST Client

        :param str host:  url of the server including protocol ('https://alpha2.shooju.com')
        :param str user: username
        :param password: api secret
        :param retries: number of attempts to make api call
        :param retry_delay: time between api call attempts (seconds)
        """
        self._url_base = host
        if base_path:
            self._url_base += base_path
        self._user = user
        self._password = password
        self._method = None
        self._retries = retries or 3
        self._retry_delay = retry_delay or 3.

    def __getattr__(self, item):
        if item not in self.ALLOWED_METHODS:
            raise AttributeError('Method %s not supported' % item)
        self._method = item
        return self._call

    def _call(self, path=None, ignore_exceptions=False, params=None, **kwargs):
        """
        Helper method that executes the HTTP request. By default, it json decodes the response and checks for API errors

        accepted keyword arguments:
            - binary_response (bool) flag indicating if the response is binary
            - data_json (dict) json payload
            - data_raw (str) raw payload
            - data (str) url encoded payload
            - params (dict) hash with the url parameters

        :param str path: resource path
        :param kwargs: keyword arguments
        :param ignore_exceptions: if True will not check shooju exception and will return raw json response
        :return: :raise ConnectionError: json response (or binary response if binary response selected)
        """
        attempt = kwargs.get('attempt', 1)
        headers = payload = None
        files = kwargs.pop('files', None)
        json_response = kwargs.get('json_response', True)
        binary_response = kwargs.get('binary_response', False)
        if 'data_json' in kwargs:
            headers = {'content-type': 'application/json'}
            payload = json.dumps(kwargs.get('data_json'))
        elif 'data_raw' in kwargs:
            payload = kwargs.get('data_raw')
        elif 'data' in kwargs:
            payload = kwargs.get('data')

        method = getattr(requests, self._method)

        url = '{base}{path}'.format(base=self._url_base, path=path)
        try:
            r = method(url, params=params or None, data=payload, headers=headers,
                       files=files, auth=(self._user, self._password))
            if r.status_code != requests.codes.ok:
                raise ConnectionError('Request failed. Error code %s' % r.status_code)
        except (requests.ConnectionError, ConnectionError) as e:
            if attempt >= self._retries:
                raise e
            else:
                time.sleep(self._retry_delay)
                kwargs['attempt'] = attempt + 1
                return self._call(path, ignore_exceptions=ignore_exceptions, files=files, params=params, **kwargs)

        if binary_response:
            return r
        elif json_response and not ignore_exceptions:
            return _check_errors(json.loads(r.content))
        elif json_response:
            return json.loads(r.content)
        return r.text


def _check_errors(response):
    """
    Checks the API response for errors. Raises error if error is found in the response.

    :param dict response: api response
    :return: :raise ConnectionError: response
    """
    if not response['success']:
        raise ShoojuApiError(_format_error(response))
    if 'responses' in response or 'series' in response:  # it's either old api bulk or new api /series request
        _check_bulk_api_errors(response.get('responses', response['series']))
    return response


def _check_bulk_api_errors(responses):
    """
    Checks bulk API response array, if a bulk response has a series_not_found error it gets removed from the response
    :param list response: array of api responses
    :raise ConnectionError:
    """
    errors = []
    for i, response in enumerate(responses):
        if response.get('error'):
            if response['error'] == 'series_not_found':
                responses[i] = None
            else:
                errors.append(_format_error(response))

    if errors:
        raise ShoojuApiError('\n'.join(errors))


def _format_error(response):
    """
    Formats the response error
    :param response: api response
    :return: formatted error string
    """
    return '%s (%s)' % (response.get('error'), response.get('description'))


class BaseJob(object):
    def __init__(self, conn, job_id, batch_size, pre_hooks=None,
                 post_hooks=None, collision_retry_timeout=60, async_mode=False):
        """
        Initialized with connection and job_id.

        Pre submit hooks and post commit hooks can be added to the job to perform actions before or after
        data is submitted to shooju. The function should accept kwargs

        :param shooju.Connection conn: API connection
        :param job_id: job id
        :param int batch_size: size of cache before uploading series to the API
        :param list pre_hooks: list of functions to be run before the job submits to shooju
        :param list post_hooks: list of functions to be run after the job submits to shooju
        :param int collision_retry_timeout: delay before do next attempt if series was already lock to update
        :param bool async_mode: indicates job will use async bulk requests
        """
        self._conn = conn
        self._job_id = job_id
        self._batch_size = batch_size
        self._cur_batch_size = 0
        self._async_mode = async_mode

        # those are values that will be sent to server
        # series_id will be the key and they will match to
        # {'fields':{},'points':{}} that !
        self._values = OrderedDict()

        self._pre_hooks = pre_hooks or []
        self._post_hooks = post_hooks or []

        self._remove = defaultdict(lambda: {'fields': False, 'points': False})
        self._collision_retry_timeout = collision_retry_timeout

    @property
    def job_id(self):
        return self._job_id

    def finish(self, submit=True):
        """
        Optionally submits and marks a job as finished. Useful for letting all interested parties know the job is done.
        This locks the job and no further actions will be possible (writing, adding logs).

        :param submit: submit the current cached data to server before finishing job
        """
        self.submit()

    def _init_get_series_dict(self, series, incr_bulk=False):
        if series not in self._values:
            self._values[series] = {'fields': {}, 'points': {}}
            if incr_bulk:
                self._cur_batch_size += 1
        else:
            if not self._values[series]['points'] and incr_bulk:
                self._cur_batch_size += 1

        return self._values[series]

    def _submit_if_bulk(self):
        """
        Submits data if we have enough  bulk
        """
        if self._cur_batch_size >= self._batch_size:
            self.submit()

    def put_points(self, series_id, points):
        """
        Accepts the series and points(Point objects)
        that will be submitted to server.

        :param series_id: series id
        :param list points: list of shooju.Point
        """
        series_values = self._init_get_series_dict(series_id, incr_bulk=True)
        for p in points:
            series_values['points'].update(p.to_dict())

        self._submit_if_bulk()

    def put_point(self, series_id, pt):
        """
        Submits a single point.

        :param shooju.Point pt: point
        :param str series_id: series id
        """
        series_values = self._init_get_series_dict(series_id, incr_bulk=True)
        series_values['points'].update(pt.to_dict())

        self._submit_if_bulk()

    def put_field(self, series_id, field_name, field_value):
        """
        Submits single field.

        :param str series_id: series id
        :param str field_name: name of the field
        :param str field_value: value of the field
        """
        series_values = self._init_get_series_dict(series_id, incr_bulk=True)
        series_values['fields'].update({field_name: field_value})

        self._submit_if_bulk()

    def put_fields(self, series_id, fields):
        """
        Submits field objects.

        :param srt series_id:
        :param dict fields: fields dict
        """
        series_values = self._init_get_series_dict(series_id, incr_bulk=True)
        series_values['fields'].update(fields)

        self._submit_if_bulk()

    def submit(self):
        pass

    def remove_points(self, series_id):
        """
        Removes all points from the series before adding the new points. This will be set until a submit is triggered
        or submit is called explicitly.

        :param series_id: series id to set the remove points flag
        """
        self._remove[series_id]['points'] = True

    def remove_fields(self, series_id):
        """
        Removes fields from the series before adding the new fields. This will be set until a submit is triggered
        or submit is called explicitly.

        :param series_id: series id to set the remove points flag
        """
        self._remove[series_id]['fields'] = True

    def add_post_submit_hook(self, fn):
        """
        Adds a hook that will be run after the cache is submitted to shooju
        :param fn: function to be executed, it should accept kwargs
        """
        self._add_hooks(self._post_hooks, fn)

    def add_pre_submit_hook(self, fn):
        """
        Adds a hook that will be run before the cache is submitted to shooju
        :param fn: function to be executed, it should accept kwargs
        """
        self._add_hooks(self._pre_hooks, fn)

    def delete(self, series_id, force=False):
        pass

    def delete_by_query(self, query, force=False):
        pass

    def _add_hooks(self, hook_list, fn):
        if not hasattr(fn, '__call__'):
            raise ValueError('hooks must be a function')
        hook_list.append(fn)

    def _run_pre_submit_hooks(self):
        for fn in self._pre_hooks:
            fn(job_id=self.job_id)

    def _run_post_submit_hooks(self, response):
        for fn in self._post_hooks:
            fn(job_id=self.job_id, response=response)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            return
        self.finish()
        return exc_type, exc_val, exc_tb


class RemoteJob(BaseJob):
    """
    Used to submit series points/fields to Shooju via a job id.

    Do not instantiate directly.  Use conn.register_job().
    """

    def finish(self, submit=True):
        """
        Optionally submits and marks a job as finished. Useful for letting all interested parties know the job is done. 
        This locks the job and no further actions will be possible (writing, adding logs).

        :param submit: submit the current cached data to server before finishing job
        """
        super(RemoteJob, self).finish(submit=submit)
        self._conn.raw.post('/jobs/{}/finish'.format(self.job_id))

    def submit(self):
        """
        Submits the current cached data to server
        """
        # the submit part should traverse all of the sids and submit them
        self._run_pre_submit_hooks()
        bulk_data = []
        for series, values in self._values.items():
            # here we will construct a BULK API call
            tmp_dict = {"type": "POST", "id": series, "body": values}
            series_remove = self._remove.pop(series, None)

            if series_remove:
                if series_remove['points'] and series_remove['fields']:
                    remove = 'all'
                elif series_remove['points']:
                    remove = 'points'
                else:
                    remove = 'fields'
                values['keep_only'] = remove

            bulk_data.append(tmp_dict)

        # we send the bulk data at once
        responses = []
        if bulk_data:
            try:
                responses = self._conn._post_bulk(bulk_data, self._job_id,
                                                  self._collision_retry_timeout, async=self._async_mode)
            finally:
                # always flush cache
                self._values = {}
                self._cur_batch_size = 0
        self._run_post_submit_hooks({'responses': responses, 'success': True})
        return True

    def delete(self, series_id, force=False):
        """
        If force parameter is False moves series to trash. Otherwise removes series.

        :param series_id: series id
        :param force: if True permanently deletes without moving to trash
        :return: True if the deletion was successful
        """
        return self._conn.shooju_api.delete_series(series_id, force, self.job_id)

    def delete_by_query(self, query, force=False):
        """
        If force==True permanently deletes all series that match the query - be careful.
        Otherwise moves these series to trash.

        :param query: query to base the deletion on
        :param force: if True permanently deletes without moving to trash
        :return: number of series deleted (moved to trash)
        """
        return self._conn.shooju_api.delete_series_by_query(query, force, self.job_id)


class DryRunJob(BaseJob):
    POINTS_PRINT_LIMIT = 5

    def finish(self, submit=True):
        super(DryRunJob, self).finish(submit=submit)
        print('Job finished')

    def submit(self):
        for series, values in self._values.items():
            if values.get('fields'):
                print('{} fields: {}'.format(series, values['fields']))
            if values.get('points'):
                points = values['points']
                print_msg = '{} points: {}'.format(
                        series,
                        list(Point(int(d), v)
                             for d, v in values['points'].items()[:min(len(points), self.POINTS_PRINT_LIMIT)]))
                if len(points) > self.POINTS_PRINT_LIMIT:
                    print_msg += ' (only {}/{} shown)'.format(self.POINTS_PRINT_LIMIT, len(points))
                print(print_msg)
        self._remove = defaultdict(lambda: {'fields': False, 'points': False})
        self._values = {}

    def delete(self, series_id, force=False):
        print('deleted series {} with force={}'.format(series_id, force))

    def delete_by_query(self, query, force=False):
        print('deleted series by query {} with force={}'.format(query, force))


class UploaderSession(object):
    """
    Used to upload files to Shooju via a session id.

    Do not instantiate directly.  Use conn.create_uploader_session().
    """

    def __init__(self, conn, session_id):
        """
        Initialized with connection and session_id.

        :param conn. Connection conn: API connection
        :param session_id: uploader session id
        """
        self._conn = conn
        self._session_id = session_id

    def upload_file(self, fp, filename):
        """
        Uploads a file object to Shooju. Returns the Shooju file id.

        :param fp: File Object to upload
        :param filename: Name of the file.  For cosmetic/retrieval purposes only.
        """
        data = self._conn.raw.post(
            '/uploader/session/{}/files'.format(self._session_id),
            files={'file': (filename, fp)}
        )
        return data['file_id'][0]


class GetBulk(object):
    """
    That class is responsible for constructing a get bulk
    request and send it to the remote API.
    """

    def __init__(self, conn):
        """
        Gets a connection object to send the data to server
        """
        self._conn = conn
        self._reqs = []

    def get_point(self, series_id, date):
        """
        Gets a point
        """
        data = {
            '_get_type': 'get_point',
            'date_format': 'milli',
            'df': to_milli(date),
            'dt': to_milli(date),
            'series_id': series_id,
        }

        self._reqs.append(data)
        return self._ticket

    def get_points(self, series_id, date_start=None, date_finish=None, max_points=10, size=None):
        """
        Get points method
        """
        if size:
            max_points = size

        data = {
            '_get_type': 'get_points',
            'date_format': 'milli',
            'df': 'MIN',
            'dt': 'MAX',
            'max_points': max_points,
            'series_id': series_id,
        }

        if date_start:
            data['df'] = to_milli(date_start)

        if date_finish:
            data['dt'] = to_milli(date_finish)


        self._reqs.append(data)
        return self._ticket

    def get_fields(self, series_id, fields=None):
        """
        Gets fields for series_id
        if fields is None then all of the fields for series is fetched
        if fields is a list then only those in the list are fetched
        """
        data = {
            '_get_type': 'get_fields',
            'series_id': series_id,
        }

        if fields:
            data['fields'] = ",".join(fields)

        self._reqs.append(data)
        return self._ticket

    def get_field(self, series_id, field):
        """
        Gets field
        """
        data = dict(_get_type='get_field',
                    series_id=series_id)

        data['fields'] = field
        self._reqs.append(data)
        return self._ticket

    def fetch(self):
        """
        That is the place we construct the get bulk query
        """
        # for now just puts the series id, but will change in future
        bulk_get = []
        for r in self._reqs:
            request = dict(r)
            bulk_get.append(request)

        if not bulk_get:
            return []

        results = self._conn._get_bulk(bulk_get)

        responses = []
        for i, series in enumerate(results):
            responses.append(self._process_response(self._reqs[i]['_get_type'], series, i))

        self._reqs = []

        return responses

    def _process_response(self, get_type, response, index):
        """
        Converts the data from the API to Points and collects fields
        """
        if response is None:  # series didn't exist
            return None

        if options.point_serializer == 'shooju_point':
            point = Point
        else:
            point = lambda dt, val: (dt, val)

        if get_type == "get_points":
            return list(map(lambda p: point(p[0], p[1]), response['points']))
        elif get_type == "get_fields" or get_type == "get_field":
            return response.get('fields', {})
        elif get_type == "get_point":
            if 'points' not in response:
                return point(float(self._reqs[index]['df']), None)
            pdata = response['points'][0]
            return point(pdata[0], pdata[1])
        else:
            return []

    @property
    def _ticket(self):
        return len(self._reqs) - 1


def flatten(iterable):
    """
    Flattens a list

    :param iterable: list of lists
    """
    for x in iterable:
        if hasattr(x, '__iter__') and not isinstance(x, basestring):
            for y in flatten(x):
                yield y
        else:
            yield x


def roundrobin(*iterables):
    """
    >>> roundrobin('ABC', 'D', 'EF')
    A D E B F C
    """
    for it in (iter(it) for it in iterables):
        for n in it:
            yield n

