"""Sends items to Squirro."""

import copy
import json
import math
import os
import sys
from ConfigParser import SafeConfigParser
from numbers import Number

from .base import SquirroClient
from .exceptions import NotFoundError

# Some magic for providing test support for the Squirro Client. squirro.common
# is not available on customer's machines, so we don't use get_injected there.
try:
    from squirro.common.dependency import DependencyNotFound, get_injected

    def get_client_cls():
        try:
            return get_injected('squirro_client_cls')
        except DependencyNotFound:
            return SquirroClient

except ImportError:
    def get_client_cls():
        return SquirroClient


class ItemUploader(object):
    """Item uploader class. Defaults are loaded from the ``.squirrorc`` file in
    the current user's home directory.

    :param token: User refresh token.
    :param project_id: Identifier of the project, optional but one of
        ``project_id`` or ``project_title`` has to be passed in.
    :param project_title:  Title of the project. This will use the first
        project found with the given title. If two projects with the same
        title exist the project being used is not predictable.
    :param object_id: Identifier of the object.
    :param source_name: Name of the source.
    :param source_ext_id: External identifier of the source, if not
        provided defaults to ``source_name``.
    :param cluster: Cluster to connect to. This only needs to be changed
        for on-premise installations.
    :param batch_size: Number of items to send in one request. This should
        be lower than 100 depending on your setup. If set to -1 the optimal
        batch size is calculated from the items. Defaults to -1.
    :param bulk_index: If set to `True` the cluster is instructed to index
        data in bulk.
    :param bulk_index_add_batch_identifier: If set to `True` the cluster is
        instructed to add a batch identifier to each item during bulk
        indexing.
    :param bulk_index_add_summary_from_body: If set to `True` the cluster is
        instructed to add the summary from the body during bulk indexing.
    :param config_file: Configuration file to use, defaults to
        ~/.squirrorc
    :param config_section: Section of the .ini file to use, defaults to
        ``squirro``.
    :param processing_config: A dictionary which contains specific instructions
        which are used while processing items for the source.
    :param source_id: Source which should be used. If passed in together with
        ``source_secret`` no source is created.
    :param source_secret: Source secret to be used with ``source_id``. If
        passed in together with ``source_id`` no source is created.

    Typical usage:

        >>> from squirro_client import ItemUploader
        >>> uploader = ItemUploader(project_title='My Project',
        ...                         token='<your token>')
        >>> items = [{'id': 'squirro-item1',
        ...           'title': 'Items arrived in Squirro!'}]
        >>> uploader.upload(items)

    Project selection:

    The `ItemUploader` creates a source in your project. The project must
    exist before the `ItemUploader` is instantiated.

    Source selection:

    The source will be created or re-used, the above parameter define
    how the source will be named.

    Configuration:

    The :class:`ItemUploader` can load its settings from a configuration file.
    The default section is ``squirro`` and may be overridden by the parameter
    ``config_section`` to allow for multiple sources/projects.

    Example configuration::

        [squirro]
        project_id = 2sic33jZTi-ifflvQAVcfw
        token = 9c2d1a9002a8a152395d74880528fbe4acadc5a1

    """

    def __init__(self, token=None, project_id=None, project_title=None,
                 object_id=None, source_name=None, source_ext_id=None,
                 cluster=None, client_cls=None, batch_size=None,
                 config_file=None, config_section=None,
                 processing_config=None, steps_config=None,
                 source_id=None, source_secret=None,
                 timeout_secs=None, **kwargs):

        self.config = None
        kwargs.update(locals())
        del kwargs['self']
        self._load_config(kwargs)
        self._validate_config()
        self.client = None

        # Do not create a new SqiurroClient if an authenticated client instance
        # has been supplied already
        if kwargs.get('client_instance'):
            self.client = kwargs.get('client_instance')
        else:
            # include 500 in the status codes for retry handling, this makes
            # the actual data loading more robust for transient failures
            # (e.g. topic  proxy outages) which are reported as 500
            self._create_squirro_client(
                client_cls,
                retry_status_forcelist=frozenset([500, 502, 503, 504]),
                timeout_secs=timeout_secs)

        self.project_id = None
        self.object_id = None
        self.source_id = source_id
        self.source_secret = source_secret
        if not all([source_id, source_secret]):
            # We only need the project_id and object_id when both the source_id
            # and source_secret are not present
            self._lookup_project_object(object_id)
            self._create_source(source_name,
                                processing_config=processing_config,
                                steps_config=steps_config)

    def _load_config(self, kwargs):
        """Loads the configuration from file and merges it with the passed-in
        arguments"""
        parser = SafeConfigParser()
        file_names = kwargs.get('config_file')
        if not file_names:
            file_names = [os.path.expanduser('~/.squirrorc')]
        parser.read(file_names)

        # initialize with defaults
        config = copy.deepcopy(self.DEFAULTS)

        # read from config-file
        config_section = kwargs.get('config_section')
        if not config_section:
            config_section = 'squirro'
        if parser.has_section(config_section):
            config.update(dict(parser.items(config_section)))

        # update with kwargs actually passed in
        config.update(dict([(k, v) for k, v in kwargs.iteritems()
                            if v is not None]))
        config = dict([(k, v) for k, v in config.iteritems()
                       if k in self.CONFIG_KEYS])

        # transform integer arguments
        for key in self.INT_OPTIONS:
            if not config.get('key') is None:
                config[key] = int(config[key])

        # adjust the cluster URL
        if config.get('cluster'):
            config['cluster'] = config['cluster'].rstrip('/')

        if not config.get('source_ext_id'):
            config['source_ext_id'] = config.get('source_name')

        self.config = config

    def _validate_config(self):
        """Validates mandatory parameters and checks invalid combination.
        Raises a `ValueError` if something is off"""

        if not all([self.config.get('source_id'),
                    self.config.get('source_secret')]):
            if not any([self.config.get('project_id'),
                        self.config.get('project_title')]):
                raise ValueError(
                    'Parameters ("project_id"/"project_title") or '
                    '("source_id" & "source_secret") is required')

        # Parameters `processing_config` and `steps_config` are not used when
        # `source_id` and `source_secret` is provided as no source will be
        # created.
        else:
            if any([self.config.get('processing_config'),
                    self.config.get('steps_config')]):
                raise ValueError(
                    'Parameters "processing_config" or "steps_config" are not '
                    'used when "source_id" and "source_secret" is provided.')

        if not self.config.get('token'):
            raise ValueError('Mandatory parameter "token" is missing')

        manual_config = [self.config.get('topic_api_url'),
                         self.config.get('user_api_url'),
                         self.config.get('provider_api_url')]
        if not self.config.get('cluster') and not all(manual_config):
            raise ValueError('Mandatory parameter "cluster" is missing')

        if all([self.config.get('project_id'),
                self.config.get('project_title')]):
            raise ValueError('Parameters "project_id" and "project_title" are '
                             'mutually exclusive')

    def _create_squirro_client(self, client_cls, **kwargs):
        """Creates a Squirro client"""
        if all([self.config.get('topic_api_url'),
                self.config.get('user_api_url'),
                self.config.get('provider_api_url')]):
            kwargs.update({
                'topic_api_url': self.config['topic_api_url'],
                'user_api_url': self.config['user_api_url']
            })
        else:
            kwargs['cluster'] = self.config['cluster']

        if not client_cls:
            client_cls = get_client_cls()

        self.client = client_cls(None, None, **kwargs)
        self.client.authenticate(refresh_token=self.config['token'])

    def _lookup_project_object(self, object_id):
        """Looks up the project either by `project_id` or `project_title`"""
        if self.config.get('project_id'):
            project_id = self.config['project_id']
            self.client.get_project(project_id)
            self.project_id = project_id
        else:
            project_title = self.config['project_title']
            projects = self.client.get_user_projects()
            for project in projects:
                if project['title'] == project_title:
                    self.project_id = project['id']
                    break

            if not self.project_id:
                raise NotFoundError('No project with title {0!r} found'
                                    .format(project_title))

        if not object_id:
            self.client.get_object(self.project_id, 'default')
            self.object_id = 'default'
        else:
            self.client.get_object(self.project_id, object_id)
            self.object_id = object_id

    def _create_source(self, source_name, processing_config=None,
                       steps_config=None):
        """Looks up or creates a source called `source_name`."""
        if not source_name:
            source_name = self.DEFAULTS['source_name']

        source_config = {
            'tenant': self.client.tenant,
            'ext_id': self.config['source_ext_id'],
            'name': source_name,
            'processing': {
                'filtering': {'enabled': False},
                'deduplication': {'enabled': True, 'policy': 'replace'},
            }
        }

        # check if bulk indexing is requested
        bulk_index = self.config.get('bulk_index')
        if bulk_index:
            source_config['bulk_index'] = bulk_index

        # bulk indexing: add batch identifier
        bulk_index_add_batch_identifier = self.config.get(
            'bulk_index_add_batch_identifier')
        if bulk_index_add_batch_identifier:
            source_config['bulk_index_add_batch_identifier'] = (
                bulk_index_add_batch_identifier)

        # bulk indexing: add summary from body
        bulk_index_add_summary_from_body = self.config.get(
            'bulk_index_add_summary_from_body')
        if bulk_index_add_summary_from_body:
            source_config['bulk_index_add_summary_from_body'] = (
                bulk_index_add_summary_from_body)

        if processing_config is not None:
            assert isinstance(processing_config, dict), 'dict required'
            source_config['processing'].update(processing_config)

        if steps_config is not None:
            assert isinstance(steps_config, list), 'list required'
            source_config['steps'] = steps_config

        res = self.client.new_subscription(self.project_id, self.object_id,
                                           'bulk', source_config, private=True)

        self.source_id = res['source_id']
        self.source_secret = res['source_secret']

    def upload(self, items):
        """Sends ``items`` to Squirro.

        :param items: A list of items. See
            :ref:`api_reference_sink_data_format` for the item format.
        """

        if not self.config.get('provider_api_url'):
            cluster = self.config['cluster']
            url = u'{0}/api/provider/v0/source/{1}/{2}'.format(
                cluster, self.source_id, self.source_secret)
        else:
            endpoint = self.config['provider_api_url']
            url = u'{0}/v0/source/{1}/{2}'.format(
                endpoint, self.source_id, self.source_secret)

        headers = {'Content-Type': 'application/json'}

        batch_size = self._get_batch_size(items)
        for idx in xrange(0, len(items), batch_size):
            for item in items[idx:idx + batch_size]:
                self._fixup_keywords(item)

            data = json.dumps(items[idx:idx + batch_size])
            res = self.client._perform_request('post', url, data=data,
                                               headers=headers)
            res.raise_for_status()

    def _get_batch_size(self, items):
        """Gets the batch size from config or calculates the optimal size based
        on the items if batch_size is set to -1.
        """
        MAX_BYTE_SIZE = 5e+7  # 50MB, allows for some json dumps overhead and
        # ES bulk action instructions

        batch_size = self.config['batch_size']

        if batch_size == -1:
            items_bytes_size = sys.getsizeof(items)
            if items_bytes_size < MAX_BYTE_SIZE:
                batch_size = len(items)
            else:
                # how many chunks do we split the items into?
                nof_chunks = math.ceil(float(items_bytes_size) / MAX_BYTE_SIZE)
                assert nof_chunks >= 1
                batch_size = min(1, math.floor(float(len(items)) / nof_chunks))

        return int(batch_size)

    def _fixup_keywords(self, item):
        """Validates and fixes keywords of `item`"""
        if item.get('keywords') is None:
            return

        keywords = item['keywords']
        for key, value in keywords.iteritems():
            if isinstance(value, (Number, basestring)):
                keywords[key] = [value]
            elif isinstance(value, list):
                keywords[key] = value
            elif isinstance(value, set):
                keywords[key] = list(value)
            else:
                raise TypeError(u'Cannot validate the keyword {0}. Type {1} '
                                u'is not supported'.format(key, type(value)))

    # default values for arguments
    DEFAULTS = {
        'source_name': 'Upload',
        'object_id': 'default',
        'cluster': 'https://demo.squirro.net',
        'batch_size': -1,  # auto calculate
        'bulk_index': False,
        'bulk_index_add_batch_identifier': False,
        'bulk_index_add_summary_from_body': False,
    }

    # options to be converted to int
    INT_OPTIONS = [
        'batch_size',
    ]

    # arguments that can be passed in the constructor/ini-file
    CONFIG_KEYS = [
        'token', 'cluster', 'project_id', 'project_title',
        'object_id', 'source_name', 'source_ext_id', 'batch_size',
        'user_api_url', 'topic_api_url', 'provider_api_url', 'bulk_index',
        'bulk_index_add_batch_identifier', 'bulk_index_add_summary_from_body',
        'source_id', 'source_secret'
    ]
