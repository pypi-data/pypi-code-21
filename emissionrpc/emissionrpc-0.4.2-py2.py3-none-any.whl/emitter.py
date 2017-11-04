
import os
import sys
from collections import OrderedDict
import json
from subprocess import Popen, PIPE

if sys.version_info >= (3, 0):
    from urllib.parse import urlsplit
elif sys.version_info < (3, 0):
    from urlparse import urlsplit

from .server import DEFAULT_ADDR, DEFAULT_PORT, Server
from .exceptions import EmissionBadParameter
from .helpers import (
    check_ids, normalize_fields_arguments, normalize_arguments,
    to_http, decoder
)


class Client(object):

    APPLICATION = "/Applications/transmission.app"

    def __init__(self,
                 address=DEFAULT_ADDR,
                 port=DEFAULT_PORT,
                 user=None,
                 password=None,
                 timeout=None):

        self._server = Server(address, port)
        self._tag = 0

    def _update_tag(self):

        self._tag = self._tag + 1

    def emission(self, method, body):

        response = self._server.execute(body)
        if response:
            return json.loads(response.text)
        else:
            return None

    def start(self, ids=None):

        method = 'torrent-start'

        arguments = OrderedDict()
        if ids:
            arguments['ids'] = check_ids(ids)

        payload = OrderedDict()
        payload['method'] = method
        payload['arguments'] = arguments
        payload['tag'] = self._tag

        self._update_tag()

        return self.emission(method, payload)

    def start_now(self, ids=None):

        method = 'torrent-start-now'

        arguments = {}
        if ids:
            arguments['ids'] = check_ids(ids)

        payload = OrderedDict()
        payload['method'] = method
        payload['arguments'] = arguments
        payload['tag'] = self._tag

        self._update_tag()

        return self.emission(method, payload)

    def stop(self, ids=None):

        method = 'torrent-stop'

        arguments = {}
        if ids:
            arguments['ids'] = check_ids(ids)

        payload = OrderedDict()
        payload['method'] = method
        payload['arguments'] = arguments
        payload['tag'] = self._tag

        self._update_tag()

        return self.emission(method, payload)

    def verify(self, ids=None):

        method = 'torrent-verify'

        arguments = {}
        if ids:
            arguments['ids'] = check_ids(ids)

        payload = OrderedDict()
        payload['method'] = method
        payload['arguments'] = arguments
        payload['tag'] = self._tag

        self._update_tag()

        return self.emission(method, payload)

    def reannounce(self, ids=None):
        method = 'torrent-reannounce'

        arguments = {}
        if ids:
            arguments['ids'] = check_ids(ids)

        payload = OrderedDict()
        payload['method'] = method
        payload['arguments'] = arguments
        payload['tag'] = self._tag

        self._update_tag()

        return self.emission(method, payload)

    def list_torrent(self, fields=['id', 'name'], ids=None):

        method = 'torrent-get'

        fields = normalize_fields_arguments(method, fields)

        arguments = {}
        arguments['fields'] = fields
        if ids:
            arguments['ids'] = check_ids(ids)

        payload = OrderedDict()
        payload['method'] = method
        payload['arguments'] = arguments
        payload['tag'] = self._tag

        self._update_tag()

        response = self.emission(method, payload)
        return response['arguments']

    def add_torrent(self, torrent, **kwargs):

        method = 'torrent-add'
        if not torrent:
            raise EmissionBadParameter('torrent should not be empty')

        args = normalize_arguments(method, kwargs)

        torrent_data = ""
        torrent_file = ""

        t_url = urlsplit(torrent)

        if t_url[0] in ('http', 'https'):
            # Problems with https
            # so download the torrent file instead to send to transmission
            _url = to_http(torrent)
            _r = self._server.download(_url)
            torrent_data = decoder(_r.content)
        elif t_url[0] == 'file':
            if not os.path.exists(t_url[2]):
                raise EmissionBadParameter("'{0}' does not exists !!".format(t_url[2]))
            torrent_file = t_url[2]
        else:
            raise EmissionBadParameter('bad http scheme')

        arguments = {k: v for k, v in args}
        if torrent_data:
            arguments['metainfo'] = torrent_data
        if torrent_file:
            arguments['filename'] = torrent_file

        payload = OrderedDict()
        payload['method'] = method
        payload['arguments'] = arguments
        payload['tag'] = self._tag

        self._update_tag()

        response = self.emission(method, payload)
        return response['arguments']

    def delete_torrent(self, ids, **kwargs):

        method = 'torrent-remove'
        if not ids:
            raise EmissionBadParameter('ids should not be empty')

        args = normalize_arguments(method, kwargs)

        arguments = {k: v for k, v in args}
        arguments['ids'] = ids

        payload = OrderedDict()
        payload['method'] = method
        payload['arguments'] = arguments
        payload['tag'] = self._tag

        self._update_tag()

        response = self.emission(method, payload)
        return response['arguments']

    def queue(self, where, ids):

        def get_method(where):

            if where == 'top':
                return 'queue-move-top'
            elif where == 'up':
                return 'queue-move-up'
            elif where == 'down':
                return 'queue-move-down'
            elif where == 'bottom':
                return 'queue-move-bottom'
            else:
                raise EmissionBadParameter('available method : top | up | down | bottom')

        if not where or not ids:
            raise EmissionBadParameter('where or ids should not be empty')

        method = get_method(where)

        arguments = {}
        arguments['ids'] = check_ids(ids)

        payload = OrderedDict()
        payload['method'] = method
        payload['arguments'] = arguments
        payload['tag'] = self._tag

        self._update_tag()

        response = self.emission(method, payload)
        return response['arguments']

    # Session

    def get_session(self):

        method = 'session-get'

        payload = OrderedDict()
        payload['method'] = method
        payload['tag'] = self._tag

        self._update_tag()

        response = self.emission(method, payload)
        return response['arguments']

    def set_session(self, **kwargs):

        method = 'session-set'

        if not kwargs:
            raise EmissionBadParameter('should have at least one argument')

        args = normalize_arguments(method, kwargs)

        arguments = {k: v for k, v in args}

        payload = OrderedDict()
        payload['method'] = method
        payload['arguments'] = arguments
        payload['tag'] = self._tag

        self._update_tag()

        response = self.emission(method, payload)
        return response['arguments']

    def stat_session(self):

        method = 'session-stats'

        payload = OrderedDict()
        payload['method'] = method
        payload['tag'] = self._tag

        self._update_tag()

        response = self.emission(method, payload)
        return response['arguments']

    def close_session(self):

        method = 'session-close'

        payload = OrderedDict()
        payload['method'] = method
        payload['tag'] = self._tag

        self._update_tag()

        response = self.emission(method, payload)
        return response

    def blocklist(self):

        method = 'blocklist-update'

        payload = OrderedDict()
        payload['method'] = method
        payload['tag'] = self._tag

        self._update_tag()

        response = self.emission(method, payload)
        return response['arguments']

    def port_test(self):

        method = 'port-test'

        payload = OrderedDict()
        payload['method'] = method
        payload['tag'] = self._tag

        self._update_tag()

        response = self.emission(method, payload)
        return response['arguments']

    def free_space(self, path):

        method = 'free-space'

        if not path:
            raise EmissionBadParameter("'path' should not be empty")

        arguments = {}
        arguments['path'] = path

        payload = OrderedDict()
        payload['method'] = method
        payload['arguments'] = arguments
        payload['tag'] = self._tag

        self._update_tag()

        response = self.emission(method, payload)
        return response['arguments']
