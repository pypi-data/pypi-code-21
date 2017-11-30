import json
import logging
import os.path
from os import environ
import pprint
from collections import Mapping, Sequence
import itertools
from itertools import islice
from builtins import map
from datetime import datetime
from past.builtins import basestring
from time import sleep, time

from requests import Session
from requests.exceptions import ConnectionError

from businessoptics.cached_file_getter import CachedTuplesCSV
from businessoptics.exceptions import APIError
from .utils import retry, join_urls, add_exception_info, strip_prefix, fix_types, ensure_list_if_string, only

log = logging.getLogger(__name__)


def id_or_name(collection_url):
    def decorator(method):
        def wrapper(self, resource_id):
            if isinstance(resource_id, basestring) and not resource_id.isdigit():
                resource_id = (self / collection_url).object_with_name(resource_id)['id']
            return method(self, resource_id)

        return wrapper

    return decorator


class Client(object):
    def __init__(self,
                 server='https://app.businessoptics.biz',
                 base_url='',
                 auth=None,
                 session=None,
                ):
        """
        Construct a new Client. authentication details can either be passed in directly:

            Client(auth=('user@example.com', 'apikey'))

        or be extracted from environment vairables:
            * BUSINESSOPTICS_EMAIL
            * BUSINESSOPTICS_APIKEY

        or from a ~/.businessoptics_client.config JSON file of the form

            { "<username>": "<apikey>" }

        """
        super(Client, self).__init__()
        self.server = server
        self.base_url = strip_prefix(base_url, server)
        assert not (auth and session), "A Client can't take both auth details and an existing session"

        if session:
            self.session = session
        else:
            self.session = Session()

            if not auth:
                auth = self.get_credentials_from_env()

            if not auth or isinstance(auth, basestring):
                auth = self.get_credentials_from_file(auth)

            assert (isinstance(auth, Sequence) and not isinstance(auth, basestring) and
                    len(auth) == 2 and
                    all(isinstance(x, basestring) for x in auth)), \
                'auth must be a pair of strings: (username, apikey)'
            self.session.headers.update({
                'Authorization': 'ApiKey {}:{}'.format(*auth)
            })

    def get_credentials_from_file(self, username):
        """
        Extract authentication credentials from a JSON file of the form

            { "<username>": "<apikey>" }

        if no username is given the special default value is used: i.e.:

            config['default']

        """
        path = os.path.join(os.path.expanduser('~'), '.businessoptics_client.config')
        try:
            with open(path) as f:
                config = json.load(f)
        except (IOError, ValueError):
            add_exception_info('Failed to load JSON credentials file at ~/.businessoptics_client.config. '
                               'Create or fix the file or specify auth=(username, apikey).')
            raise

        if not username:
            try:
                username = config['default']
            except KeyError:
                raise Exception('No auth specified and no default username found in config.')

        try:
            apikey = config[username]
        except KeyError:
            raise Exception('No API key found for username %s in config' % username)

        return (username, apikey)


    def get_credentials_from_env(self):
        """
        Extract authentication credentials from environment variables.

        Auth details extracted from:
          * BUSINESSOPTICS_EMAIL
          * BUSINESSOPTICS_APIKEY
        """
        username = environ.get('BUSINESSOPTICS_EMAIL')
        apikey = environ.get('BUSINESSOPTICS_APIKEY')
        if username and apikey:
            return (username, apikey)
        else:
            return None

    @classmethod
    def at(cls, client, base_url=None):
        if base_url is None:
            base_url = client.base_url
        return cls(server=client.server,
                   base_url=base_url,
                   session=client.session)

    @classmethod
    def local(cls, auth=('development@businessoptics.biz', 'development'), *args, **kwargs):
        return cls(server='http://app.businessoptics.dev', auth=auth, *args, **kwargs)

    @classmethod
    def staging(cls, *args, **kwargs):
        return cls(server='https://app.businessoptics.net', *args, **kwargs)

    @classmethod
    def production(cls, *args, **kwargs):
        # Production is the default server
        return cls(*args, **kwargs)

    @retry(5, ConnectionError, log)
    def request(self, method, url='', **kwargs):
        url = join_urls(self.server, self.base_url, url)
        response = self.session.request(method, url, **kwargs)
        if response.status_code in (502, 503, 504):
            raise ConnectionError('Server returned code %s' % response.status_code)
        try:
            result = response.json()
        except ValueError:
            raise APIError(url, response, message='Failed to parse JSON')
        if result.get('status') != 'ok' or result.get('error') or result.get('state') == 'error':
            raise APIError(url, response, response_json=result)
        return result

    def get(self, url='', **kwargs):
        kwargs.setdefault('allow_redirects', True)
        return self.request('GET', url, **kwargs)

    def options(self, url='', **kwargs):
        kwargs.setdefault('allow_redirects', True)
        return self.request('OPTIONS', url, **kwargs)

    def head(self, url='', **kwargs):
        kwargs.setdefault('allow_redirects', False)
        return self.request('HEAD', url, **kwargs)

    def post(self, url='', **kwargs):
        return self.request('POST', url, **kwargs)

    def put(self, url='', **kwargs):
        return self.request('PUT', url, **kwargs)

    def patch(self, url='', **kwargs):
        return self.request('PATCH', url, **kwargs)

    def delete(self, url='', **kwargs):
        return self.request('DELETE', url, **kwargs)

    def __div__(self, other):
        result = Client.at(self)
        result.base_url = join_urls(self.base_url, other)
        return result

    def __truediv__(self, other):
        return self.__div__(other)

    @property
    def root(self):
        return Client.at(self, '')

    @property
    def api(self):
        return Client.at(self, '/api/v2')

    @property
    def internal(self):
        return Client.at(self, '/api/internal')

    @id_or_name('/api/v2/workspace')
    def workspace(self, resource_id):
        workspace = Workspace.at(self.api / 'workspace' / resource_id)
        workspace.id = resource_id
        return workspace

    def dashboard(self, resource_id):
        return Dashboard.at(self.api / 'dashboard' / resource_id)

    def dataset(self, resource_id):
        return Dataset.at(self.api / 'dataset' / resource_id)

    @id_or_name('/api/v2/datacollection')
    def datacollection(self, resource_id):
        return DataCollection.at(self.api / 'datacollection' / resource_id)

    @property
    def full_url(self):
        return join_urls(self.server, self.base_url)

    def __repr__(self):
        return self.__class__.__name__ + '@' + self.full_url

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def object_with_name(self, name):
        collection = self.get('?expand=objects')['objects']
        return only(x for x in collection if x['name'].strip().lower() == name.strip().lower())


class Workspace(Client):

    def __init__(self, *args, **kwargs):
        super(Workspace, self).__init__(*args, **kwargs)
        self.id = None

    def query(self, ideas, parameters=None, **extra_post_fields):
        ideas = ensure_list_if_string(ideas)
        parameters = fix_types(parameters or {})

        response = self.post('query', json=dict(knowledge_parameters=parameters,
                                                ideanames=ideas,
                                                **extra_post_fields))

        uri = response['uri']
        log.info('Started query in workspace %s for %s idea(s) including %s: %s',
                 self.id, len(ideas), ideas[0], join_urls(self.server, uri))
        query = Query.at(self, uri)
        query.ideas = ideas
        return query

    def quick(self, ideas, parameters=None, **extra_post_fields):
        ideas = ensure_list_if_string(ideas)
        parameters = fix_types(parameters or {})

        response = self.post('quick', json=dict(knowledge_parameters=parameters,
                                                ideanames=ideas,
                                                **extra_post_fields))

        log.info('Performed quick query in workspace %s for %s idea(s) including %s: %s',
                 self.id, len(ideas), ideas[0], self.server)

        return Quick(response)

    dashboard = id_or_name('dashboard')(Client.dashboard)


class Awaitable(Client):
    desired_state = 'complete'

    def __init__(self, *args, **kwargs):
        super(Awaitable, self).__init__(*args, **kwargs)
        self.state = None
        self.start_time = time()

    def await(self):
        while self.state != self.desired_state:
            state = self.get()['state']
            if state != self.state:
                log.debug('%s state is now %s', self, state)
            self.state = state
            if state != self.desired_state:
                sleep(2)
        log.info('Completed %s in %s seconds', self, round(time() - self.start_time, 1))


class Query(Awaitable):
    def __init__(self, *args, **kwargs):
        super(Query, self).__init__(*args, **kwargs)
        self.ideas = None

    def result(self, information_id=None):
        ideas = self.ideas
        if information_id is None:
            if ideas and len(ideas) == 1:
                information_id = ideas[0]
            else:
                raise ValueError(
                    'You must specify an information identifier for a result unless only one idea was queried')
        self.await()
        return IdeaResult.at(self / 'result' / information_id)

    def tuples(self, information_id=None, limit=None, offset=0, auto_parse=True):
        return self.result(information_id).tuples(limit, offset, auto_parse)


class Quick(object):
    """
    Encapsulates a quick query. Conforms to the standard query API.
    """

    def __init__(self, response):
        self.response = response

    def result(self, information_id):
        return QuickResult(self.response['results'][information_id])

    def tuples(self, information_id=None, limit=None, offset=0, auto_parse=True):
        return self.result(information_id).tuples(limit, offset, auto_parse)

    def await(self):
        """
        Simply a stub for query API compatibility
        """
        return


class QuickResult(object):
    """
    Provides a result API for quick results
    """
    def __init__(self, response):
        self.response = response

    def tuples(self, limit=None, offset=0, auto_parse=True):
        response = self.response
        limit = HasTuples.check_infinite_limit(limit)

        datetime_dimensions = []
        if auto_parse:
            dimensions = response['structure']
            datetime_dimensions = [d['name'] for d in dimensions
                                   if d['type'].upper() == 'DATETIME']

        tuples = response['tuples'][offset:limit]
        for dim in datetime_dimensions:
            for tup in tuples:
                value = tup[dim]
                datetime_format = '%Y-%m-%dT%H:%M:%S'
                if 'T' not in value:
                    datetime_format = datetime_format.replace('T', ' ')
                tup[dim] = datetime.strptime(value, datetime_format)

        return tuples


class HasTuples(Client):
    def dimensions_dict(self):
        return {d['name']: d['type'] for d in self.get()['dimensions']}

    def tuples(self, limit=None, offset=0, auto_parse=True):
        return list(self.tuple_generator(limit, offset, auto_parse))

    def tuple_generator(self, limit=None, offset=0, auto_parse=True):
        datetime_dimensions = []
        if auto_parse:
            dimensions = self.get()['dimensions']
            datetime_dimensions = [d['name'] for d in dimensions
                                   if d['type'].upper() == 'DATETIME']
        limit = self.check_infinite_limit(limit)

        while True:
            request_limit = min(2000, limit)
            response = self.get('tuples', params=dict(limit=request_limit, offset=offset))
            tuples = response['tuples']
            for tup in tuples:
                for dim in datetime_dimensions:
                    value = tup[dim]
                    if value is None:
                        continue
                    datetime_format = '%Y-%m-%dT%H:%M:%S'
                    if 'T' not in value:
                        datetime_format = datetime_format.replace('T', ' ')
                    tup[dim] = datetime.strptime(value, datetime_format)
                yield tup

            offset += request_limit
            limit -= request_limit
            if offset >= response['meta']['count'] or limit <= 0:
                return

    @staticmethod
    def check_infinite_limit(limit):
        if limit in (0, -1, None):
            limit = 99999999
        return limit

    def stream(self):
        return map(json.loads,
                   self.session.get(join_urls(self.server, self.base_url, 'stream'),
                                    stream=True
                                    ).iter_lines())

    def to_df(self):
        import pandas  # you must install this separately
        import numpy

        csv_path = CachedTuplesCSV(self).path()
        dimension_types = self.dimensions_dict()
        type_map = dict(STRING=str, DATETIME=str, INTEGER=numpy.int64, REAL=numpy.float64, BOOLEAN=bool)
        pandas_types = {k: type_map[v.upper()] for k, v in dimension_types.items()}
        date_columns = [k for k, v in dimension_types.items()
                        if v.upper() == 'DATETIME']
        return pandas.read_csv(csv_path,
                               dtype=pandas_types,
                               parse_dates=date_columns,
                               keep_default_na=False)


class IdeaResult(HasTuples):
    def reingest_into_existing_dataset(self, dataset_id, **dimension_mappings):
        """
        Reingest the tuples from this result into an existing dataset with the given ID as an upsert.
        Dimension mappings should be specified as <result dimension>=<dataset dimension>.
        Note that sometimes the result dimension name is not exactly what you see in the query result.
        For example you should use value_renamed instead of value. Same for [start_|end_]datetime.
        """
        log.info('Reingesting %s into dataset %s', self, dataset_id)

        # Create default mappings where the names and types match on both sides
        dataset_dimensions = set(self.dataset(dataset_id).dimensions_dict().items())
        result_dimensions = set(self.dimensions_dict().items())
        matching_dimensions = dataset_dimensions & result_dimensions
        mappings = [dict(csv_name=name, db_name=name)
                    for name, _ in matching_dimensions
                    if name not in dimension_mappings]
        mappings += [dict(csv_name=key, db_name=value)
                     for key, value in dimension_mappings.items()]
        response = self.post('reingest_now', json=dict(dataset_id=dataset_id,
                                                       mappings=mappings))
        return DataUpdate.at(self, response['uri'])


class Dashboard(Client):
    def query_parameters(self):
        return Query.at(self, self.post('query_parameters')['uri'])

    def parameter_options(self):
        query = self.query_parameters()
        result = []

        def add_parameters_from(obj):
            for p in obj['parameters']:
                add_parameter(p)

        def add_parameter(parameter):
            def add_to_result():
                parameter['options_tuples'] = tuples
                result.append(parameter)

            if parameter['type'] == 'section':
                add_parameters_from(parameter)
            elif parameter['type'] == 'multi_select':
                options_idea = parameter['options_idea']
                tuples = query.tuples(options_idea)
                tuples = [{selector['idea']: tup[selector['dimension']]
                           for selector in parameter['selectors']}
                          for tup in tuples]
                add_to_result()
            else:
                idea = parameter['idea']
                if parameter['type'] == 'hidden':
                    values = [parameter['value']]
                elif parameter['type'] == 'select':
                    options = parameter['options']
                    options_source = options['options_source']
                    if options_source == 'idea':
                        dimension = options['dimension']
                        tuples = query.tuples(options['idea'])
                        values = [t[dimension] for t in tuples]
                    elif options_source == 'list':
                        values = options['options']
                    else:
                        raise ValueError('Unknown options source %s' % options_source)
                else:
                    raise ValueError('Unknown parameter type %s', parameter['type'])
                tuples = [{idea: value} for value in values]
                add_to_result()

        add_parameters_from(self.get('display'))
        return result


class Dataset(HasTuples):
    @property
    def tableset(self):
        return Tableset.at(self / 'tableset')


class Tableset(Client):
    def upload_tuples(self, tuples, columns=None, truncate_columns=()):
        if isinstance(tuples, Sequence) and len(tuples) == 0:
            log.info('Uploaded 0 tuples total to %s', self.full_url)
            return []

        column_objects = {c['field_name']: c for c in
                          self.get('column?expand=objects')['objects']}

        # If a single tuple is passed, wrap it in a list
        if (isinstance(tuples, Mapping) or
                isinstance(tuples, Sequence) and
                (isinstance(tuples[0], basestring) or not isinstance(tuples[0], (Sequence, Mapping)))):
            tuples = [tuples]

        columns = ensure_list_if_string(columns)

        if columns is not None:
            tuples = (dict(zip(columns, t)) for t in tuples)

        batch_size = 2000
        count = 0
        milestones = itertools.chain([4000, 10000, 20000, 50000],
                                     itertools.count(100000, 100000))
        current_milestone = 2000
        responses = []
        tuples = iter(tuples)  # ensures islice properly exhausts the iterator
        while True:
            batch = list(islice(tuples, batch_size))
            count += len(batch)
            if not batch:
                break
            batch = fix_types(batch)
            for tup in batch:
                for key, value in tup.items():
                    if value is None or (value == '' and column_objects[key]['field_type'].lower() != 'string'):
                        tup[key] = column_objects[key]['default']
                    if isinstance(value, basestring) and len(value) > 250:
                        if key in truncate_columns:
                            tup[key] = value[:250]
                        else:
                            raise ValueError(
                                'The key %r has a value of length %s. The maximum allowed is 250. ' %
                                (key, len(value)) +
                                'Set truncate_columns=%r in upload_tuples to automatically truncate before uploading. '
                                % (list(truncate_columns) + [key],) +
                                'Full tuple preview:\n%s' % pprint.pformat(tup)[:10000])
            responses.append(self.post('tuples', json={'tuples': batch}))
            if count >= current_milestone:
                log.info('Uploaded %s tuples so far to %s', count, self.full_url)
                current_milestone = next(milestones)
        log.info('Uploaded %s tuples total to %s', count, self.full_url)
        return responses

    def delete_tuples(self, filters=()):
        return self.delete('tuples', json={'filters': filters})


class DataUpdate(Awaitable):
    desired_state = 'done'


class DataCollection(Client):
    @id_or_name('dataset')
    def dataset(self, resource_id):
        return Dataset.at(self.api / 'dataset' / resource_id)
