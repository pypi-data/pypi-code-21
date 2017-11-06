# -*- coding: utf-8 -*-
"""
    mackerel.client
    ~~~~~~~~~~~~~~~

    Mackerel client implemented by Python.

    Ported from `mackerel-client-ruby`.
    <https://github.com/mackerelio/mackerel-client-ruby>

    :copyright: (c) 2014 Hatena, All rights reserved.
    :copyright: (c) 2015 Shinya Ohyanagi, All rights reserved.
    :copyright: (c) 2016 Iskandar Setiadi, All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
import os
import logging
import requests
import simplejson as json
from mackerel.host import Host
from mackerel.monitor import MonitorHost, MonitorExternal, \
    MonitorService, MonitorConnectivity


class MackerelClientError(Exception):
    pass


class MackerelMonitorError(Exception):
    pass


class Client(object):
    #: Mackerel apikey error message.
    ERROR_MESSAGE_FOR_API_KEY_ABSENCE = 'API key is absent. Set your API key in a environment variable called MACKEREL_APIKEY.'
    #: Log format.
    debug_log_format = (
        '[%(asctime)s %(levelname)s][%(pathname)s:%(lineno)d]: %(message)s'
    )

    def __init__(self, logger=None, **kwargs):
        """Construct a Mackerel client.

        :param mackerel_origin: API endpoint
        :param mackerel_api_key: API key
        """
        self.origin = kwargs.get('mackerel_origin', 'https://mackerel.io')
        api_key = kwargs.get('mackerel_api_key', None)
        # Check api_key from environment variable
        if api_key is None:
            api_key = os.environ.get('MACKEREL_APIKEY', None)
        # Fail if api_key is still None
        if api_key is None:
            raise MackerelClientError(self.ERROR_MESSAGE_FOR_API_KEY_ABSENCE)

        self.api_key = api_key
        if logger is None:
            logging.basicConfig(level=logging.INFO,
                                format=self.debug_log_format)
            self.logger = logging.getLogger('mackerel.client')
        else:
            self.logger = logger

    ## HOST SECTION
    def get_hosts(self, **kwargs):
        """Get hosts.

        :param service: Service name
        :param roles: Service role
        :param name: Host name
        """
        uri = '/api/v0/hosts.json'
        params = {}
        if kwargs.get('service', None):
            params['service'] = kwargs.get('service')

        if kwargs.get('roles', None):
            params['roles'] = kwargs.get('roles')

        if kwargs.get('name', None):
            params['name'] = kwargs.get('name')

        hosts = self._request(uri, params=params)
        return [Host(**host) for host in hosts['hosts']]

    def get_host(self, host_id):
        """Get registered host.

        :param host_id: Host id
        """
        uri = '/api/v0/hosts/{0}'.format(host_id)
        data = self._request(uri)

        return Host(**data['host'])

    def update_host_status(self, host_id, status):
        """Update host status.

        :param host_id: Host id
        :param status: `standby`, `working`, `maintenance` or `poweroff`
        """
        if status not in ['standby', 'working', 'maintenance', 'poweroff']:
            raise MackerelClientError('no such status: {0}'.format(status))

        uri = '/api/v0/hosts/{0}/status'.format(host_id)
        headers = {'Content-Type': 'application/json'}
        params = json.dumps({'status': status})
        data = self._request(uri, method='POST', headers=headers, params=params)

        return data

    def retire_host(self, host_id):
        """Retire host.

        :param host_id: Host id
        """
        uri = '/api/v0/hosts/{0}/retire'.format(host_id)
        headers = {'Content-Type': 'application/json'}
        data = self._request(uri, method='POST', headers=headers)

        return data

    ## HOST METRICS SECTION
    def post_metrics(self, metrics):
        """Post metrics.

        :param metrics: Metrics
        """
        uri = '/api/v0/tsdb'
        headers = {'Content-Type': 'application/json'}
        params = json.dumps(metrics)
        data = self._request(uri, method='POST', headers=headers, params=params)

        return data

    def get_latest_metrics(self, host_ids, names):
        """Get latest metrics.

        :param host_ids: Host id list
        :param names: Metrics list
        """
        hosts_query = '&'.join(['hostId={0}'.format(id) for id in host_ids])
        names_query = '&'.join(['name={0}'.format(name) for name in names])
        uri = '/api/v0/tsdb/latest?{0}&{1}'.format(hosts_query, names_query)

        data = self._request(uri)

        return data

    def get_host_metrics(self, host_id, name, from_, to):
        """Get host metrics.

        :param host_id: Host id
        :param name: Metric name
        :param from_: Start of the time period you want metrics for (unix time)
        :param to: End of the time period you want metrics for (unix time)
        :return: Host metrics
        """
        uri = '/api/v0/hosts/{0}/metrics?name={1}&from={2}&to={3}'.format(host_id, name, from_, to)
        data = self._request(uri)

        return data

    ## SERVICE METRICS SECTION
    def post_service_metrics(self, service_name, metrics):
        """Post service metrics.

        :param service_name: Registered service name
        :param metrics: Metrics list
        """
        uri = '/api/v0/services/{0}/tsdb'.format(service_name)
        headers = {'Content-Type': 'application/json'}
        params = json.dumps(metrics)
        data = self._request(uri, method='POST', headers=headers, params=params)

        return data

    ## MONITORING SECTION
    def get_monitors(self, ids=None):
        """Get monitors.

        :param ids: List of Monitor Ids to be searched, if it doesn't exist, return None as value
        """
        uri = '/api/v0/monitors'
        data = self._request(uri)

        monitors = []

        for entity in data['monitors']:
            if entity['type'] == 'host':
                monitors.append(MonitorHost(**entity))
            elif entity['type'] == 'service':
                monitors.append(MonitorService(**entity))
            elif entity['type'] == 'external':
                monitors.append(MonitorExternal(**entity))
            elif entity['type'] == 'connectivity':
                monitors.append(MonitorConnectivity(**entity))
            else:
                raise MackerelMonitorError('Type is not in defined types')

        if not ids:
            return monitors

        # If list of monitor ids is specified, search it by order
        monitor_targets = {}
        for id in ids:
            target = None
            for monitor in monitors:
                if monitor.id == id:
                    target = monitor
                    break
            monitor_targets[id] = target

        return monitor_targets

    def create_monitor(self, monitor_params):
        """Create monitor.

        :param monitor_params: Parameter list of new Monitor
        """
        uri = '/api/v0/monitors'
        headers = {'Content-Type': 'application/json'}
        params = json.dumps(monitor_params)

        data = self._request(uri, method='POST', headers=headers, params=params)

        return data

    def update_monitor(self, monitor_id, monitor_params):
        """Update monitor.

        :param monitor_id: Monitor id
        :param monitor_params: Parameter list of updated Monitor
        """
        uri = '/api/v0/monitors/{0}'.format(monitor_id)
        headers = {'Content-Type': 'application/json'}
        params = json.dumps(monitor_params)

        data = self._request(uri, method='PUT', headers=headers, params=params)

        return data

    def delete_monitor(self, monitor_id):
        """Delete monitor.

        :param monitor_id: Monitor id
        """
        uri = '/api/v0/monitors/{0}'.format(monitor_id)
        headers = {'Content-Type': 'application/json'}

        data = self._request(uri, method='DELETE', headers=headers)

        return data

    def _request(self, uri, method='GET', headers=None, params=None):
        """Request to mackerel.

        :param uri: Request uri
        :param method: HTTP Method
        :param headers: HTTP Headers
        :param params: HTTP Body or params
        """
        uri = '{0}{1}'.format(self.origin, uri)
        if headers is None:
            headers = {'X-Api-Key': self.api_key}
        else:
            headers.update({'X-Api-Key': self.api_key})

        self.logger.debug('{0} {1} {2}'.format(method, uri, params))
        if method == 'GET':
            res = requests.get(uri, headers=headers, params=params)
        elif method == 'POST':
            res = requests.post(uri, headers=headers, data=params)
        elif method == 'PUT':
            res = requests.put(uri, headers=headers, data=params)
        elif method == 'DELETE':
            res = requests.delete(uri, headers=headers, data=params)
        else:
            message = '{0} is not supported.'.format(method)
            raise NotImplementedError(message)

        self.logger.debug('Response from {0} is {1}'.format(self.origin,
                                                            res.status_code))
        if res.status_code != 200:
            message = '{0} {1} failed: {2}'.format(method, uri, res.status_code)
            raise MackerelClientError(message)
        data = json.loads(res.content)

        return data
