'''pastry_client handles the interaction with the chef server api'''

import os
import yaml
import requests
import threading
from contextlib import contextmanager

from pastry.utils.auth import signed_headers
from pastry.exceptions import HttpError


class PastryClient(object):
    '''
    PastryClient is used by the resources to send requests to chef.
    You can use the PastryClient to initialize the config to use for the
    chef server.
    '''
    server = None
    organization = None
    client = None
    keypath = None
    verify = None
    session = None
    initialized = False

    @classmethod
    def initialize(cls, server, organization, client, keypath, verify):
        '''
        Initializes the server connection info

        :param server: The url for the chef server e.g. https://my.chef.server
        :param organization: The name of the cheff org to use
        :param client: The client/username to use
        :param keypath: The path to the pem for the client/user
        :param verify: Verify the ssl cert on requests
        :type server: string
        :type organization: string
        :type client: string
        :type keypath: string
        :type verify: boolean
        '''
        cls.server = server
        cls.organization = organization
        cls.client = client
        cls.keypath = keypath
        cls.verify = verify
        cls.session = requests.Session()
        cls.session.mount(cls.server, requests.adapters.HTTPAdapter(
            pool_connections=50,
            pool_maxsize=50
        ))
        cls.initialized = True

    @classmethod
    @contextmanager
    def context(cls, organization=None):
        '''
        Context manager to override the default org

        :param organization: The name of the org to use for the command
        :type organization: string

        .. note::
            org is temporarily stored in current_thread()._pastry_org

        .. code-block::

            with PastryClient.context(organization='myorg'):
                print Nodes.exists('mynode')
        '''
        if not cls.initialized:
            cls.load_config()
        threading.current_thread()._pastry_org = organization
        yield
        del threading.current_thread()._pastry_org

    @classmethod
    def load_config(cls, config_path=None):
        '''
        Load server config from a yaml file

        If no config_path is specified it will try to load config from
        ``$HOME/.chef/pastry.yaml``

        .. note::

            This method is automatically called if an http requests is made and
            the client has not yet been initialised

        :param config_path: The path to the config file on the local filesystem
        :type config_path: string
        '''
        if not config_path:
            config_path = os.path.join(
                os.environ['HOME'], '.chef', 'pastry.yaml')
        if not os.path.exists(config_path):
            raise ValueError(
                'PastryClient not initialized and %s does not exist' %
                config_path
            )
        with open(config_path, 'r') as config_file:
            config = yaml.safe_load(config_file.read())
        cls.initialize(
            config['server'],
            config['organization'],
            config['client'],
            config['keypath'],
            config.get('verify', True)
        )

    @classmethod
    def get_url(cls, endpoint):
        '''
        Fetches the server and updates the endpoint with the organization

        :param endpoint: The endpoint being called on the chef server
        :type endpoint: string
        :return: The server url and updated endpoint
        :rtype: tuple
        '''
        if not cls.initialized:
            cls.load_config()
        org = getattr(
            threading.current_thread(), '_pastry_org', cls.organization)
        return cls.server, (endpoint % {'org': org})

    @classmethod
    def call(cls, endpoint, method='GET', data=None):
        '''
        Send an http request to the chef server api

        :param endpoint: The endpoint for the resource being called
        :param method: The HTTP method
        :param data: The body of the request
        :type endpoint: string
        :type method: string
        :type data: hash
        :return: The json response from the server
        :rtype: hash
        '''
        server, path = cls.get_url(endpoint)
        headers = signed_headers(
            cls.client,
            cls.keypath,
            path.split('?', 1)[0],
            method=method,
            data=data
        )
        headers['Connection'] = 'close'
        kwargs = {
            'headers': headers,
            'verify': cls.verify,
        }
        if data:
            kwargs['json'] = data

        resp = {
            'GET': cls.session.get,
            'POST': cls.session.post,
            'PUT': cls.session.put,
            'DELETE': cls.session.delete
        }[method]('%s%s' % (server, path), **kwargs)
        if not resp.ok:
            raise HttpError(resp.text, resp.status_code)
        return resp.json()

    @classmethod
    def status(cls):
        '''
        Check the chef server status

        :return: The json response form the server
        :type: hash
        '''
        resp = cls.session.get(
            '%s/_status' % cls.server,
            verify=cls.verify,
            headers={'Connection': 'close'}
        )
        if not resp.ok:
            raise HttpError(resp.text, resp.status_code)
        return resp.json()
