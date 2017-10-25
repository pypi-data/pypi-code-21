import os

from fizzgun.core import Producer, SourceAdapter
from fizzgun.impl.mitm_plugin import onboarding_extensions
from mitmproxy.tools.main import mitmdump


class MitmAdapter(SourceAdapter):
    """
    Converts mitmproxy request format to fizzgun's format
    """
    MAP = {'body': 'content'}

    def convert(self, request):
        full_state = request.get_state()

        norm_request = {k: self._decode(full_state[self.MAP.get(k, k)])
                        for k in self.FIELDS if k in full_state or k in self.MAP}
        if '?' in norm_request['path']:
            norm_request['path'], norm_request['query'] = norm_request['path'].split('?', 1)
        else:
            norm_request['query'] = None
        return norm_request

    @classmethod
    def _decode(cls, value):
        if isinstance(value, bytes):
            return value.decode('utf-8')
        if hasattr(value, '__iter__'):
            return [cls._decode(v) for v in value]
        return value


class FizzgunHandler(object):
    """
    A 'mitmproxy' handler that connects mitmproxy with fizzgun
    """
    def __init__(self, connector, mitm_plugin):
        self._producer = Producer(MitmAdapter(), connector)
        self._mitm = mitm_plugin

    # @concurrent
    def request(self, flow):
        session_id = flow.metadata['proxyauth'][0] if 'proxyauth' in flow.metadata else None
        self._producer.produce(flow.request, session_id)


class MitmPlugin(object):
    INSTANCE = None

    def __init__(self, config):
        self.cfg = config
        self.settings = config.mitmproxy
        self.fizzgun_handler = None
        MitmPlugin.INSTANCE = self

    def start(self, producer_output):
        onboarding_extensions.setup(self.cfg.report['directory'])
        self.fizzgun_handler = FizzgunHandler(producer_output, self)

        args = [
            '-p', str(self.settings['port']),
            '--onboarding-host', 'fizzgun.it'
        ]
        if self.settings['insecure']:
            args.append('--insecure')
        if self.settings['track_sessions']:
            args.append('--nonanonymous')
        if self.settings['http_connect_ignore']:
            args.extend(['--ignore', self.settings['http_connect_ignore']])

        args.extend(['-s', self._bootstrap()])
        mitmdump(args)

    @classmethod
    def _bootstrap(cls):
        return os.path.abspath(os.path.join(os.path.dirname(__file__), 'bootstrap.py'))
