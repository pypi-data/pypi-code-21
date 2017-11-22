from __future__ import absolute_import, division, print_function, unicode_literals
import os
import tempfile
from collections import defaultdict, OrderedDict
import datetime
import time
import sys
from logging import getLogger
import re
from .points_serializers import shooju_point, NANOSECONDS, Point
from .common import *

if NUMPY_INSTALLED:
    from .points_serializers import np_array

if PANDAS_INSTALLED:
    from .points_serializers import pd_series

import requests

KEY_RE = re.compile(r'\{([\w\d\.]+)}')

if sys.version_info[0] >= 3:
    basestring = str


# global lib options
class Options(object):

    def __init__(self, disable_sjts=False, disable_msgpack=False, points_serializer=shooju_point):
        self._disable_sjts = self._disable_msgpack = None
        self.series_serializer = self.default_serializer = None
        self.point_serializer = points_serializer

        self._set_serializers(disable_sjts=disable_sjts, disable_msgpack=disable_msgpack)

    @staticmethod
    def _get_serializer(disable_sjts=True, disable_msgpack=True):
        if not disable_sjts and sjts is None:
            raise Exception('sjts module is not installed')
        elif not disable_msgpack and msgpack is None:
            raise Exception('msgpack module is not installed')

        if not disable_sjts:
            return sjts
        elif not disable_msgpack:
            return msgpack
        return json_serializer

    def _set_serializers(self, disable_sjts=None, disable_msgpack=None):
        disable_sjts = self._disable_sjts if disable_sjts is None else disable_sjts
        disable_msgpack = self._disable_msgpack if disable_msgpack is None else disable_msgpack

        self.default_serializer = self._get_serializer(disable_msgpack=disable_msgpack)
        self.series_serializer = self._get_serializer(disable_sjts=disable_sjts, disable_msgpack=disable_msgpack)

        self._disable_sjts = disable_sjts
        self._disable_msgpack = disable_msgpack

    @property
    def disable_sjts(self):
        return self._disable_sjts

    @disable_sjts.setter
    def disable_sjts(self, value):
        self._set_serializers(disable_sjts=value)

    @property
    def disable_msgpack(self):
        return self._disable_msgpack

    @disable_msgpack.setter
    def disable_msgpack(self, value):
        self._set_serializers(disable_msgpack=value)

    @property
    def point_serializer(self):
        return self._point_serializer

    @point_serializer.setter
    def point_serializer(self, val):
        assert callable(val), 'point_serializer must be callable'
        self._point_serializer = val


options = Options(disable_sjts=sjts is None, disable_msgpack=msgpack is None)

logger = getLogger('shooju_client')


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
            conn.raw.delete('/alerts/topics/series/types/alert')

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
        if PANDAS_INSTALLED:
            if not hasattr(self, '_pandas_formatter'):
                self._pandas_formatter = PandasFormatter(self.shooju_api)
            return self._pandas_formatter
        else:
            return None



    def search(self, query='', date_start=None, date_finish=None, fields=None, max_points=0, size=None,
               per_page=10, sort_on=None, sort_order=None, query_size=None, sort=None, serializer=None):
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
        :param sort_on: field used to sort the results (deprecated)
        :param sort_order: order of search results. (deprecated)
        :param sort: field(s) to sort on; formatted as comma-delimited list of <FIELD> <DIRECTION> where <DIRECTION> is one of "asc" and "desc".
        :param serializer: points serializer function; use one of shooju.points_serializers.* 
        :return: a dict hashed by series id with a list of Points per series id
        :rtype: dict
        """
        warnings.warn('"search()" is deprecated (use scroll())', DeprecationWarning)
        serializer = options.point_serializer if serializer is None else serializer
        deserialize_response_to_numpy = _desiralize_points_response_directly_to_numpy(serializer)

        data = self.shooju_api.search_series(query, date_start, date_finish, max_points, per_page=per_page,
                                             fields=fields, size=size, sort_on=sort_on, sort_order=sort_order,
                                             query_size=query_size, sort=sort,
                                             deserialize_response_to_numpy=deserialize_response_to_numpy)
        return self._process_search_response(data, serializer)

    def get_series(self, series_query, fields=None, df=None, dt=None, max_points=0, snapshot_date=None,
                   reported_date=None, extra_params=None, serializer=None, ):
        """
        Retrieves fields and points for a series query. Can select time range. If series does not exist returns
        None

        :param str series_query: query that returns 1 series
        :param fields: list of fields to retrieve; use ['*'] for all non-meta
        :param df: date FROM for points; can be datetime(), date(), 'MAX', 'MIN', or relative date format
        :param dt: date TO for points; can be datetime(), date(), 'MAX', 'MIN', or relative date format
        :param max_points: number of points to retrieve per series; use -1 for all
        :param datetime.datetime snapshot_date: If passed returns
                                    the historic snapshot of how the series looked at that datetime
        :param datetime.datetime reported_date:  If passed returns
                                    the historic snapshot of how the series looked as of the reported date
        :param dict extra_params: extra parameters; refer to API Documentation
        :param serializer: points serializer function; use one of shooju.points_serializers.*
        :return: series dict with series_id and optional points and fields keys
        """
        serializer = options.point_serializer if serializer is None else serializer
        deserialize_response_to_numpy = _desiralize_points_response_directly_to_numpy(serializer)

        data = self.shooju_api.get_single_series(series_query=series_query, df=df, dt=dt,
                                                 max_points=max_points,
                                                 snapshot_date=snapshot_date,
                                                 fields=fields,
                                                 extra_params=extra_params,
                                                 reported_date=reported_date,
                                                 deserialize_response_to_numpy=deserialize_response_to_numpy)

        if data and 'points' in data:
            data['points'] = serializer(data['points'])

        return data if data is not None else None

    def scroll(self, query='', fields=None, df=None, dt=None, max_points=0,
               operators=None, sort=None, serializer=None, max_series=None, extra_params=None,
               scroll_batch_size=2500, date_start=None, date_finish=None):
        """
        Performs a scroll search. Function is a generator, yields series

        Usage::

            for series in conn.scroll_series():
                # do something with the dict

        :param query: query that returns 0+ series
        :param fields: list of fields to retrieve; use ['*'] for all non-meta
        :param df: date FROM for points; can be datetime(), date(), 'MAX', 'MIN', or relative date format
        :param dt: date TO for points; can be datetime(), date(), 'MAX', 'MIN', or relative date format
        :param max_points: number of points to retrieve per series; use -1 for all
        :param operators: array of series operators
        :param sort: field(s) to sort on; formatted as comma-delimited list of <FIELD> <DIRECTION> where <DIRECTION> is one of "asc" and "desc".
        :param serializer: points serializer function; use one of shooju.points_serializers.* 
        :param max_series: maximum number of series to return
        :param extra_params: extra parameters; refer to API Documentation
        :param scroll_batch_size: number of series to retrieve per single API request
        
        """
        if date_start is not None:
            df = date_start
        if date_finish is not None:
            dt = date_finish
            
        scroll = max_series is None or max_series > scroll_batch_size

        serializer = options.point_serializer if serializer is None else serializer
        deserialize_response_to_numpy = _desiralize_points_response_directly_to_numpy(serializer)

        r = self.shooju_api.search_series(query, date_start, date_finish, max_points=max_points,
                                          fields=fields, scroll=scroll,
                                          scroll_batch_size=scroll_batch_size if scroll else None,
                                          operators=operators, sort=sort,
                                          deserialize_response_to_numpy=deserialize_response_to_numpy,
                                          url_params=extra_params, per_page=max_series if not scroll else None)
        scroll_id = r.get('scroll_id') if scroll else None
        series_left = r['total'] if scroll else min(max_series, r['total'])

        while series_left > 0:
            for s in self._process_search_response(r, serializer):
                yield s
            series_left -= len(r['series'])
            if series_left:
                r = self.shooju_api.scroll_series(scroll_id)

    def get_points(self, series_id, date_start=None, date_finish=None, max_points=10,
                   snapshot_job_id=None, snapshot_date=None, size=None, reported_date=None, serializer=None):
        """
        Long-term deprecated; get_series() using query sid="{series_id}" instead.
        
        Retrieves points for a series id. Can select time range. If series does not exist returns
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
        :param datetime.datetime reported_date:  If not passed returns latest data, otherwise returns
                                    the historic snapshot of how the series looked as of the reported date
        :param serializer: points serializer function; use one of shooju.points_serializers.* 
        :return: points represented by `serializer` type
        :rtype: list, numpy.array, pandas.Series
        """
        if size is not None:
            max_points = size
        serializer = options.point_serializer if serializer is None else serializer
        deserialize_response_to_numpy = _desiralize_points_response_directly_to_numpy(serializer)

        data = self.shooju_api.get_single_series(series_id=series_id, df=date_start, dt=date_finish,
                                                 max_points=max_points,
                                                 snapshot_job_id=snapshot_job_id,
                                                 snapshot_date=snapshot_date,
                                                 reported_date=reported_date,
                                                 deserialize_response_to_numpy=deserialize_response_to_numpy)

        return serializer(data.get('points', [])) if data is not None else None

    def get_point(self, series_id, dt, snapshot_job_id=None, snapshot_date=None, reported_date=None, serializer=None):
        """
        Deprecated
        """
        warnings.warn('"get_point()" is deprecated', DeprecationWarning)

        serializer = options.point_serializer if serializer is None else serializer
        points = self.get_points(series_id, dt, dt,
                                 snapshot_job_id=snapshot_job_id,
                                 snapshot_date=snapshot_date,
                                 reported_date=reported_date, serializer=serializer)
        if points is None:
            return None
        return points[0] if len(points) >= 1 else serializer([(int(to_milli(dt)), None)])[0]

    def get_field(self, series_id, field, snapshot_job_id=None, snapshot_date=None):
        """
        Deprecated
        """
        warnings.warn('"get_field()" is deprecated', DeprecationWarning)
        fields = self.get_fields(series_id, [field], snapshot_job_id=snapshot_job_id, snapshot_date=snapshot_date)
        if fields is None:
            return None
        return fields.get(field)

    def get_fields(self, series_id, fields='*', snapshot_job_id=None, snapshot_date=None,):
        """
        Long-term deprecated; get_series() using query sid="{series_id}" instead.
        
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
        data = self.shooju_api.get_single_series(series_id=series_id, size=0, fields=fields,
                                                 snapshot_job_id=snapshot_job_id, snapshot_date=snapshot_date, )
        if data is None:
            return None
        return data.get('fields', {})

    def get_reported_dates(self, series_id=None, series_query=None, job_id=None, processor=None, df=None, dt=None):
        """
        Retrieves reported dates for one of the following (use only one): series_id, series_query, job_id, processor.  Dates returned can be limited via df/dt.

        :param series_id: returns reported dates written for that series_id
        :param series_query: returns reported dates written for that series_id; takes precedence over series_id
        :param job_id: return reported dates written by that job
        :param processor:  return reported dates for series written by that processor
        :param df: datetime to start the dates array
        :param dt: datetime to finish the dates array
        :return: list of reported dates
        """
        if series_query is not None:
            series_id = u'${}'.format(series_query)
        reported_dates = self.shooju_api.get_reported_dates(series_id=series_id, job_id=job_id, processor=processor,
                                                            df=df, dt=dt).get('reported_dates') or []
        return list(map(milli_to_datetime, reported_dates))

    def register_job(self, description, notes="", batch_size=1,
                     dry_run=False):
        """
        Registers a job in Shooju. A job is used to write series.

        :param str description: brief description
        :param str notes: notes about the job
        :param int batch_size: indicates the size of the buffer before creating new series in the server
        :param bool dry_run: if True data will no be send to Shooju. it just will be printed.
        :return: a RemoteJob instance
        :rtype: shooju.RemoteJob
        """
        if len(description) < 3:
            raise ValueError('description should be longer than 3 characters')

        if not dry_run:
            data = self.shooju_api.register_job(description, notes)
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

    def download_file(self, file_id, filename=None):
        """
        Downloads a file. If no `filename` is provided, a temporary file is created

        :param file_id: file id
        :param filename: file name for downloaded file
        :return: File instance
        """
        return self.shooju_api.download_file(file_id, filename)

    def _process_search_response(self, data, serializer):
        """
        Helper method to convert a api series search response to the module data structures
        :param data: api series response
        :param serializer: points serializer function; use one of shooju.points_serializers.* 
        :return: array of series objects
        :rtype: list
        """
        results = list()
        for s in data['series']:
            s.setdefault('fields', {})
            if 'points' in s:
                s['points'] = serializer(s['points'])
            results.append(s)
        return results


class PandasFormatter(object):

    NULL_VALUE = 'null'

    def __init__(self, api_client):
        """

        :param shooju.ShoojuApi api_client: ShoojuApi instance
        """
        self.api_client = api_client

    def search(self, query='', date_start=None, date_finish=None,
               max_points=0, fields=None, per_page=10, key_field=None, size=None, query_size=None,
               operators=None):
        """
        Performs a block search and returns the results in pandas.DataFrame.

        :param query: query to perform
        :param per_page: number of series to return
        :param date_start: start date for points
        :param date_finish: end date for points
        :param max_points: number of points to retrieve per series
        :param size: number of points to retrieve per series (deprecated)
        :param fields: list of fields to retrieve
        :param query_size: number of series to return (deprecated)
        :param key_field: fields which will be used as pandas DataFrame column name (series_id by default)
        :param operators: array of series operators
        :return: a pandas.DataFrame
        :rtype: pandas.DataFrame

        """
        key_field = key_field if key_field != 'series_id' else None  # no needs to explicitly pull this

        if key_field:
            fields = self._get_fields_in_key(key_field)
        response = self.api_client.search_series(query, date_start, date_finish, max_points,
                                                 per_page=per_page, fields=fields, size=size,
                                                 query_size=query_size, operators=operators)
        return self._process_search_request(response, key_field=key_field)

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
        if not response['series']:
            return pandas.DataFrame()

        has_fields = any(r.get('fields') for r in response['series']) and not key_field
        has_points = any(r.get('points') for r in response['series'])

        if has_points and has_fields:
            data = list()
            fields_by_sid = dict()
            series_by_dates = defaultdict(dict)

            for s in response['series']:
                fields_by_sid[s['series_id']] = s.get('fields', dict())
                for p in s.get('points', []):
                    series_by_dates[p[0]][s['series_id']] = p[1]
            for dt_milli, series_values in series_by_dates.items():
                dt = pandas.Timestamp(dt_milli * NANOSECONDS)
                for series_id in fields_by_sid:
                    value = series_by_dates[dt_milli].get(series_id)
                    row = dict(fields_by_sid[series_id])
                    row.update({'date': dt, 'points': value, 'series_id': series_id})
                    data.append(row)
        elif has_points:
            data = dict()
            if key_field:
                fields_in_key = self._get_fields_in_key(key_field)
            for s in response['series']:
                dates, values = list(), list()
                if key_field:
                    key = self._get_column_name(key_field, fields_in_key, s.get('fields', {}))
                else:
                    key = s['series_id']
                for p in s.get('points', []):
                    dates.append(p[0] * NANOSECONDS)
                    values.append(p[1])
                data[key] = pandas.Series(index=pandas.DatetimeIndex(dates), data=values)
        else:
            data = list()
            for s in response['series']:
                data.append(dict(series_id=s['series_id'], **s.get('fields', dict())))

        return pandas.DataFrame(data=data)

    def _get_column_name(self, key_field, fields_in_key, fields):
        if not fields_in_key:  # no fields were requested, probably user error like {test
            return self.NULL_VALUE

        # one field case, no format, just return the value fo the field
        if '{' not in key_field:
            value = fields.get(key_field)
            value = value if value is not None else self.NULL_VALUE
            return value

        field_dict = {}
        for field, value in fields.items():
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


def _parse_dt(d, default):
    if d is not None and not isinstance(d, six.string_types):
        d = to_milli(d)
    elif d is None:
        d = default
    return d


class ShoojuApi(object):
    """
    Class used to encapsulate Shooju API methods. Methods return the json decoded response from the server and raise
    an error if the response had errors.
    """

    API_SERIES = '/series'
    API_SERIES_WRITE = '/series/write'
    API_SERIES_DELETE = '/series/delete'
    API_REPORTED_DATES = '/series/reported_dates'
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

    def get_single_series(self, series_id=None, series_query=None, df=None, dt=None,
                          max_points=None, fields=None, snapshot_job_id=None, snapshot_date=None,
                          reported_date=None, deserialize_response_to_numpy=None, extra_params=None, **kwargs):
        """
        Retrieves series

        :param str series_id: series id
        :param str series_query: series query
        :param datetime.datetime df: start date for points
        :param datetime.datetime dt:  end date for points
        :param int max_points: number of points to retrieve
        :param list fields: list of fields to retrieve
        :param int snapshot_job_id: job identifier. If not passed returns latest data, otherwise returns
                                    the historic snapshot of how the series looked after the job.
        :param datetime.datetime snapshot_date: If not passed returns latest data, otherwise returns
                                    the historic snapshot of how the series looked at that datetime.
        :param datetime.datetime reported_date: If not passed returns latest data, otherwise returns
                                    the historic snapshot of how the series looked as of the reported date.
        :param deserialize_response_to_numpy: if True will deserialize sjts body into numpy points array
        :param dict extra_params: extra url parameters to pass to api call
        :return: api response
        :rtype: dict
        """
        assert series_id or series_query, 'either one of series_id, series_query must be passed'
        max_points = max_points or kwargs.get('size')
        return self.series_read(series_ids=[series_id] if series_id is not None else None,
                                series_queries=[series_query] if series_query is not None else None,
                                df=df, dt=dt, max_points=max_points,
                                fields=fields, snapshot_job_id=snapshot_job_id,
                                snapshot_date=snapshot_date, reported_date=reported_date,
                                deserialize_response_to_numpy=deserialize_response_to_numpy,
                                extra_params=extra_params)[0]

    def series_read(self, series_ids=None, series_queries=None, series_requests=None,
                    df=None, dt=None, max_points=None, fields=None, snapshot_job_id=None,
                    snapshot_date=None, reported_date=None, deserialize_response_to_numpy=None, extra_params=None):
        """
        Executes series read request

        :param list series_ids: array of series ids to fetch
        :param list series_queries: array of series queries ids to fetch
        :param list series_requests: array of series ids and its parameters
        :param datetime.datetime df: start date for points
        :param datetime.datetime dt:  end date for points
        :param int max_points: number of points to retrieve
        :param list fields: list of fields to retrieve
        :param int snapshot_job_id: job identifier. If not passed returns latest data, otherwise returns
                                    the historic snapshot of how the series looked after the job.
        :param datetime.datetime snapshot_date: If not passed returns latest data, otherwise returns
                                    the historic snapshot of how the series looked at that datetime.
        :param datetime.datetime reported_date: If not passed returns latest data, otherwise returns
                                    the historic snapshot of how the series looked as of the reported date.
        :param deserialize_response_to_numpy: if True will deserialize sjts body into numpy points array
        :param dict extra_params: extra url parameters to pass to api call
        :return: api response
        :rtype: dict
        """
        deserializer_params = dict()
        if deserialize_response_to_numpy:
            deserializer_params['use_numpy'] = True
        url_params = {
            'date_format': 'milli',
            'df': _parse_dt(df, 'MIN') if df is not None else None,
            'dt': _parse_dt(dt, 'MAX') if dt is not None else None,
            'snapshot_job_id': snapshot_job_id,
            'snapshot_date': to_milli(snapshot_date) if snapshot_date else None,
            'reported_date': to_milli(reported_date) if reported_date else None,
        }

        if fields is not None:
            url_params['fields'] = ','.join(fields)

        if max_points is not None:
            url_params['max_points'] = max_points

        if extra_params:
            url_params.update(extra_params)

        client_kwargs = {
            'ignore_exceptions': True,
            'deserializer': options.series_serializer,
            'deserializer_params': deserializer_params,
            'params': url_params
        }

        if series_ids is not None:
            data_json = {'series_ids': series_ids}
        elif series_requests is not None:
            data_json = {'series': series_requests}
        elif series_queries is not None:
            data_json = {'series_queries': series_queries}
        else:
            raise AssertionError('either one of the following parameters must be passed: '
                                 'series_ids, series_ids_requests, series_queries')
        client_kwargs['data_json'] = data_json

        response = self.client.post('/series', **client_kwargs)
        if 'series' not in response:  # looks like entire bulk request failed
            _check_errors(response)
        _check_bulk_api_errors(response['series'])
        return response['series']

    def series_write(self, data, job_id=None, collision_retry_timeout=60,
                     async=False):
        """
        Writes series data

        :param list data: array of series objects to write
        :param int job_id: job id
        :param float collision_retry_timeout: lock write timeout
        :param bool async: indicates that fields should be written asynchronously
        """
        deserializer = options.default_serializer
        serializer = options.series_serializer

        # by this logic we trying to retry failed sub-requests and bring all responses together in to same order
        req_by_index = {i: r for i, r in enumerate(data)}
        resp_by_index = {}
        params = {k: v for k, v in {'job_id': job_id, 'async': int(async), 'date_format': 'milli'}.items() if k}

        req_index_to_send = req_by_index.keys()
        attempts_left = 3

        while req_index_to_send and attempts_left:
            req_index_to_send = sorted(req_index_to_send)
            req_index_to_send_again = list()
            attempts_left -= 1

            requests_to_send = [req_by_index[r] for r in req_index_to_send]
            payload = {'series': requests_to_send}
            response = self.client.post('/series/write', ignore_exceptions=True, data_json=payload,
                                        params=params, deserializer=deserializer, serializer=serializer)
            if 'responses' not in response:  # looks like entire bulk request failed
                _check_errors(response)

            for i, resp in enumerate(response['responses']):
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

    def register_job(self, description, notes='', source='python'):
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
                      sort_order='asc', operators=None, size=None, query_size=None, sort=None,
                      deserialize_response_to_numpy=None, url_params=None):
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
        :param deserialize_response_to_numpy: if True will deserialize sjts body into numpy points array
        :param url_params: additional url_params
        :return: dict with the api response
        """
        if size is not None:
            max_points = size

        deserializer_params = dict()
        if deserialize_response_to_numpy:
            deserializer_params['use_numpy'] = True

        params = {
            'query': query,
            'date_format': 'milli',
            'df': _parse_dt(date_start, 'MIN'),
            'dt': _parse_dt(date_finish, 'MAX'),
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

        if sort:
            params['sort'] = sort
        elif sort_on:
            params['sort'] = '{} {}'.format(sort_on, sort_order)

        if operators:
            params['operators'] = '@{}'.format('@'.join(operators))

        if url_params:
            params.update(url_params)

        return self.client.get(self.API_SERIES, deserializer=options.series_serializer, params=params,
                               deserializer_params=deserializer_params)

    def get_reported_dates(self, series_id=None, job_id=None, processor=None, df=None, dt=None):
        """
        Retrieves reported dates.

        :param series_id: returns reported dates written for that series_id
        :param job_id: return reported dates written by that job
        :param processor:  return reported dates for series written by that processor
        :param df: datetime to start the dates array
        :param dt: datetime to finish the dates array
        :return: list of reported dates
        """
        assert series_id or job_id or processor, 'At least one of series_id, job_id or processor parameters required'
        params = {
            'series_id': series_id,
            'job_id': job_id,
            'processor': processor,
            'date_format': 'milli'
        }
        if df is not None:
            params['df'] = to_milli(df)
        if dt is not None:
            params['dt'] = to_milli(dt)
        return self.client.get(self.API_REPORTED_DATES, params=params)

    def scroll_series(self, scroll_id):
        """
        Series scroll endpoint. Retrieves the next scroll data. Should be used in tandem with
        search_series with scroll flag set to True.

        Scroll has finished when no more series are returned

        :param scroll_id: scroll id
        :return: api response
        :rtype: dict
        """
        response = self.client.get(self.API_SERIES, deserializer=options.series_serializer,
                                   params={'scroll_id': scroll_id})
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

    def _call(self, path=None, ignore_exceptions=False, params=None,
              serializer=None, deserializer=None, deserializer_params=None, **kwargs):
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
        :param serializer: serializer instance to send data to api
        :param deserializer: serializer instance to receive data from api
        :param deserializer_params: mapping with additional response deserialization params
        :return: :raise ConnectionError: json response (or binary response if binary response selected)
        """
        serializer = serializer or options.default_serializer
        deserializer = deserializer or options.default_serializer
        deserializer_params = deserializer_params or dict()
        attempt = kwargs.get('attempt', 1)
        headers, payload = dict(), None
        files = kwargs.pop('files', None)
        json_response = kwargs.get('json_response', True)
        binary_response = kwargs.get('binary_response', False)
        if 'data_json' in kwargs:
            headers = {'Sj-Send-Format': serializer.__name__}
            if serializer.__name__ == 'json':  # for backward compatibility
                headers.update({'content-type': 'application/json'})
            payload = serializer.dumps(kwargs.get('data_json'))
        elif 'data_raw' in kwargs:
            payload = kwargs.get('data_raw')
        elif 'data' in kwargs:
            payload = kwargs.get('data')
        headers['Sj-Receive-Format'] = deserializer.__name__

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
            return _check_errors(deserializer.loads(r.content, **deserializer_params))
        elif json_response:
            return deserializer.loads(r.content, **deserializer_params)
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


def _desiralize_points_response_directly_to_numpy(serializer):
    # small optimization for faster de-serialization if sjts is available
    if not SJTS_SUPPORTS_NUMPY or not NUMPY_INSTALLED or sjts is not options.series_serializer:
        return False
    deserialize_response_to_numpy = False
    if serializer is np_array or (PANDAS_INSTALLED and serializer is pd_series):
        deserialize_response_to_numpy = options.series_serializer is sjts if SJTS_INSTALLED is not None else False
    return deserialize_response_to_numpy


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
        self._requests = OrderedDict()

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

    def _init_get_series_dict(self, series, delete=False, reported_date=None):
        key = series, reported_date
        if key not in self._requests:
            self._requests.setdefault(key, {})
            self._cur_batch_size += 1

        if not delete and self._requests[key].get('op') != 'post':
            self._requests[key] = {'fields': {}, 'points': {}, 'op': 'post'}
        elif delete:
            self._requests[key] = {'force': False, 'op': 'delete'}

        return self._requests[key]

    def _submit_if_bulk(self):
        """
        Submits data if we have enough bulk
        """
        if self._cur_batch_size >= self._batch_size:
            self.submit()

    def put_points(self, series_id, points):
        """
        Writes the points for the series_id.  To submit immediately, set batch_size to 1 or use submit().

        :param series_id: series id
        :param list points: list of shooju.Point
        """
        request = self._init_get_series_dict(series_id)
        for p in points:
            request['points'].update(p.to_dict())

        self._submit_if_bulk()

    def put_reported_points(self, series_id, reported_date, points):
        """
        Writes the points for the series_id and associates them with reported_date.  To submit immediately, set batch_size to 1 or use submit().

        :param series_id: series id
        :param datetime.datetime reported_date: date reported
        :param list points: list of shooju.Point
        """
        request = self._init_get_series_dict(series_id, reported_date=reported_date)
        for p in points:
            request['points'].update(p.to_dict())

        self._submit_if_bulk()

    def put_point(self, series_id, pt):
        """
        Writes the point for the series_id.  To submit immediately, set batch_size to 1 or use submit().

        :param shooju.Point pt: point
        :param str series_id: series id
        """
        request = self._init_get_series_dict(series_id)
        request['points'].update(pt.to_dict())

        self._submit_if_bulk()

    def put_field(self, series_id, field_name, field_value):
        """
        Writes the field_value under the field_name for the series_id.  To submit immediately, set batch_size to 1 or use submit().

        :param str series_id: series id
        :param str field_name: name of the field
        :param str field_value: value of the field
        """
        request = self._init_get_series_dict(series_id)
        request['fields'].update({field_name: field_value})

        self._submit_if_bulk()

    def put_fields(self, series_id, fields):
        """
        Writes the fields for the series_id.  To submit immediately, set batch_size to 1 or use submit().

        :param srt series_id: series id
        :param dict fields: fields dict
        """
        request = self._init_get_series_dict(series_id)
        request['fields'].update(fields)

        self._submit_if_bulk()

    def submit(self):
        pass

    def remove_points(self, series_id):
        """
        Sets a flag to remove all points from the series_id before the next put_point(s) call.

        :param series_id: series id to set the remove points flag
        """
        self._remove[series_id]['points'] = True

    def remove_fields(self, series_id):
        """
        Sets a flag to remove all points from the series_id before the next put_field(s) call.

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
        """
        Deletes series_id.

        :param series_id: series id
        :param force: if True permanently deletes without moving to trash
        :return: True if the deletion was successful
        """
        self._init_get_series_dict(series=series_id, delete=True)['force'] = force
        self._submit_if_bulk()

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
        Submits the currently queued data.
        """
        # the submit part should traverse all of the sids and submit them
        self._run_pre_submit_hooks()
        bulk_data = []
        for (series, reported_date), values in self._requests.items():
            # here we will construct a BULK API call
            if values['op'] == 'delete':
                tmp_dict = {"type": "DELETE", "series_id": series, 'force': values['force']}
            else:  # post
                points = list(sorted(six.iteritems(values['points'])))
                tmp_dict = {"type": "POST", "series_id": series}
                if points:
                    tmp_dict['points'] = points
                if values['fields']:
                    tmp_dict['fields'] = values['fields']

            series_remove = self._remove.pop(series, None)

            if series_remove:
                if series_remove['points'] and series_remove['fields']:
                    remove = 'all'
                elif series_remove['points']:
                    remove = 'points'
                else:
                    remove = 'fields'
                tmp_dict['keep_only'] = remove

            if reported_date is not None:
                tmp_dict['reported_date'] = to_milli(reported_date)

            bulk_data.append(tmp_dict)

        # we send the bulk data at once
        responses = []
        if bulk_data:
            try:
                responses = self._conn.shooju_api.series_write(bulk_data, job_id=self._job_id,
                                                               collision_retry_timeout=self._collision_retry_timeout,
                                                               async=self._async_mode)
            finally:
                # always flush cache
                self._requests = {}
                self._cur_batch_size = 0
        self._run_post_submit_hooks({'responses': responses, 'success': True})
        return True

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
        for (series, reported_date), values in self._requests.items():
            if reported_date is not None:
                series = '{} @ {}'.format(series, reported_date)
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
        self._requests = {}

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
        self._query_mode = None
        self._points_serializer_by_ix = dict()

    def get_point(self, series_id, date, reported_date=None, snapshot_job_id=None, snapshot_date=None, serializer=None):
        """
        Deprecated
        """
        warnings.warn('"get_point()" is deprecated', DeprecationWarning)
        self.queries_mode = False
        data = {
            '_get_type': 'get_point',
            'date_format': 'milli',
            'df': _parse_dt(date, 'MIN'),
            'dt': _parse_dt(date, 'MAX'),
            'series_id': series_id,
            'max_points': 1,
            'snapshot_job_id': snapshot_job_id,
            'snapshot_date': to_milli(snapshot_date) if snapshot_date else None
        }

        if reported_date:
            data['reported_date'] = reported_date
        self._points_serializer_by_ix[len(self._reqs)] = options.point_serializer \
            if serializer is None else serializer
        self._reqs.append(data)
        return self._ticket

    def get_points(self, series_id, date_start=None, date_finish=None, max_points=10,
                   size=None, snapshot_job_id=None, snapshot_date=None, reported_date=None, serializer=None):
        """
        Long-term deprecated; get_series() using query sid="{series_id}" instead.

        Retrieves points for a series id. Can select time range. If series does not exist it returns
        None

        :param str series_id: series id
        :param datetime.datetime date_start: get points < date
        :param int snapshot_job_id: job identifier. If not passed returns latest data, otherwise returns
        :param datetime.datetime date_finish: get points > date
                                    the historic snapshot of how the series looked after the job.
        :param datetime.datetime snapshot_date: If not passed returns latest data, otherwise returns
                                    the historic snapshot of how the series looked at that datetime.
        :param int max_points: number of points to get
        :param int size: number of points to get (this parameter is deprecated, use max_points)
        :param datetime.datetime reported_date:  If not passed returns latest data, otherwise returns
                                    the historic snapshot of how the series looked as of the reported date
        :param serializer: points serializer function; use one of shooju.points_serializers.* 
        :return: points represented by `serializer` type
        :rtype: list, numpy.array, pandas.Series
        """
        self.queries_mode = False

        if size:
            max_points = size

        data = {
            '_get_type': 'get_points',
            'date_format': 'milli',
            'df': _parse_dt(date_start, 'MIN'),
            'dt': _parse_dt(date_finish, 'MAX'),
            'max_points': max_points,
            'series_id': series_id,
            'snapshot_job_id': snapshot_job_id,
            'snapshot_date': to_milli(snapshot_date) if snapshot_date else None,
        }

        if reported_date:
            data['reported_date'] = to_milli(reported_date)

        self._points_serializer_by_ix[len(self._reqs)] = options.point_serializer \
            if serializer is None else serializer
        self._reqs.append(data)
        return self._ticket

    def get_fields(self, series_id, fields=None, snapshot_job_id=None, snapshot_date=None,):
        """
        Long-term deprecated; get_series() using query sid="{series_id}" instead.
        """
        self.queries_mode = False

        data = {
            '_get_type': 'get_fields',
            'series_id': series_id,
            'snapshot_job_id': snapshot_job_id,
            'snapshot_date': to_milli(snapshot_date) if snapshot_date else None,
        }

        if fields:
            data['fields'] = ",".join(fields)

        self._reqs.append(data)
        return self._ticket

    def get_field(self, series_id, field, snapshot_job_id=None, snapshot_date=None, ):
        """
        Deprecated
        """
        warnings.warn('"get_field()" is deprecated', DeprecationWarning)
        self.queries_mode = False

        data = {
            '_get_type': 'get_field',
            'series_id': series_id,
            'snapshot_job_id': snapshot_job_id,
            'snapshot_date': to_milli(snapshot_date) if snapshot_date else None
        }

        data['fields'] = field
        self._reqs.append(data)
        return self._ticket


    def get_series(self, series_query, fields=None, df=None, dt=None, max_points=0, snapshot_date=None,
                   reported_date=None, extra_params=None, serializer=None, ):
        """
        Retrieves fields and points for a series query. Can select time range. If series does not exist returns
        None

        :param str series_query: query that returns 1 series
        :param fields: list of fields to retrieve; use ['*'] for all non-meta
        :param df: date FROM for points; can be datetime(), date(), 'MAX', 'MIN', or relative date format
        :param dt: date TO for points; can be datetime(), date(), 'MAX', 'MIN', or relative date format
        :param max_points: number of points to retrieve per series; use -1 for all
        :param datetime.datetime snapshot_date: If passed returns
                                    the historic snapshot of how the series looked at that datetime
        :param datetime.datetime reported_date:  If passed returns
                                    the historic snapshot of how the series looked as of the reported date
        :param dict extra_params: extra parameters; refer to API Documentation
        :param serializer: points serializer function; use one of shooju.points_serializers.*
        :return: series dict with series_id and optional points and fields keys
        """
        self.queries_mode = True
        data = {
            '_get_type': 'get_points',
            'date_format': 'milli',
            'df': _parse_dt(df, 'MIN') if df is not None else None,
            'dt': _parse_dt(dt, 'MAX') if dt is not None else None,
            'max_points': max_points,
            'query': series_query,
            'snapshot_date': to_milli(snapshot_date) if snapshot_date else None,
        }
        if extra_params:
            data.update(extra_params)

        if reported_date:
            data['reported_date'] = to_milli(reported_date)

        if fields:
            data['fields'] = ",".join(fields)

        self._points_serializer_by_ix[len(self._reqs)] = options.point_serializer \
            if serializer is None else serializer
        self._reqs.append(data)

    def fetch(self):
        """
        That is the place we construct the get bulk query
        """
        # for now just puts the series id, but will change in future
        deserialize_response_to_numpy = False

        bulk_get = []
        for i, r in enumerate(self._reqs):
            request = dict(r)
            bulk_get.append(request)

            # check if we can (and should) deserialize directly to numpy array
            if not deserialize_response_to_numpy and i in self._points_serializer_by_ix:
                points_serializer = self._points_serializer_by_ix[i]
                deserialize_response_to_numpy = _desiralize_points_response_directly_to_numpy(points_serializer)

        if not bulk_get:
            return []

        deserializer_params = dict()
        if deserialize_response_to_numpy:
            deserializer_params['use_numpy'] = True

        results = self._conn.shooju_api.series_read(series_requests=bulk_get if not self.queries_mode else None,
                                                    series_queries=bulk_get if self.queries_mode else None,
                                                    deserialize_response_to_numpy=deserialize_response_to_numpy)
        responses = []
        for i, series in enumerate(results):
            responses.append(self._process_response(self._reqs[i]['_get_type'], series, i))

        self._reqs = []
        self._query_mode = None
        self._points_serializer_by_ix.clear()

        return responses

    @property
    def queries_mode(self):
        return self._query_mode

    @queries_mode.setter
    def queries_mode(self, val):
        assert self._query_mode is None or self._query_mode == val, \
            'Can not mix series queries and series requests'

        self._query_mode = val

    def _process_response(self, get_type, response, index):
        """
        Converts the data from the API to Points and collects fields
        """
        if response is None:  # series didn't exist
            return None

        points_serializer = self._points_serializer_by_ix[index] if index in self._points_serializer_by_ix else None

        if self.queries_mode:
            if 'points' in response:
                response['points'] = points_serializer(response['points'])
            return response

        if get_type == "get_points":
            return points_serializer(response.get('points', []))
        elif get_type == "get_fields" or get_type == "get_field":
            return response.get('fields', {})
        elif get_type == "get_point":
            if 'points' not in response:
                return points_serializer([(float(self._reqs[index]['df']), None)])[0]
            pdata = response['points'][0]
            return points_serializer([(pdata[0], pdata[1])])[0]
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

