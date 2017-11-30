from __future__ import absolute_import

import json

from collections import defaultdict
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.web import http
from twisted.web.client import Agent, HTTPConnectionPool

from treq.client import HTTPClient

from vumi.config import ConfigText
from vumi.transports.httprpc import HttpRpcTransport
from vxwassup.throttle import ThrottleManager


class VxWassupTransportConfig(HttpRpcTransport.CONFIG_CLASS):
    api_url = ConfigText(
        'The base url of the transport', required=True, static=True)
    token = ConfigText(
        'The token to authenticate with', required=True, static=True)


TPS_LIMIT = 20

throttle = ThrottleManager()


class VxWassupTransport(HttpRpcTransport):
    """
    HTTP transport for Wassup
    """
    transport_type = 'sms'
    CONFIG_CLASS = VxWassupTransportConfig
    clock = reactor

    def setup_transport(self):
        super(VxWassupTransport, self).setup_transport()
        self.stash_registry = defaultdict(list)
        self.pool = self.pool_factory(self.clock)
        throttle.start()

    def teardown_transport(self):
        super(VxWassupTransport, self).teardown_transport()
        throttle.stop()

    @classmethod
    def pool_factory(cls, reactor):
        pool = HTTPConnectionPool(reactor, persistent=True)
        pool.maxPersistentPerHost = TPS_LIMIT

    @classmethod
    def agent_factory(cls, reactor, pool=None):  # pragma: nocover
        """For swapping out the Agent we use in tests."""
        return Agent(reactor, pool=pool)

    @inlineCallbacks
    def handle_raw_inbound_message(self, message_id, request):
        try:
            payload = json.load(request.content)
            hook = payload.get('hook', {})
            cb = {
                'message.direct_outbound.status': self.handle_delivery_report,
                'message.group_outbound.status': self.handle_delivery_report,
                'message.direct_inbound': self.handle_inbound_notification,
                'message.group_inbound': self.handle_inbound_notification,
            }.get(hook.get('event'), None)
            if cb:
                yield cb(message_id, payload, request)
            else:
                yield self.finish_request(
                    message_id, json.dumps({
                        'error': 'Unable to handle payload'}),
                    code=http.BAD_REQUEST)
        except ValueError:
            self.finish_request(
                message_id, json.dumps({
                    'error': 'Unable to handle request'}),
                code=http.BAD_REQUEST)

    @inlineCallbacks
    def handle_delivery_report(self, message_id, payload, request):
        data = payload.get('data', {})
        wassup_message_id = data.get('message_uuid')
        metadata = data.get('message_metadata', {})
        our_message_id = metadata.get('junebug_message_id')

        status = data.get('status')
        if status == 'sent':
            self.publish_ack(user_message_id=our_message_id,
                             sent_message_id=wassup_message_id)
        elif status == 'delivered':
            self.publish_delivery_report(user_message_id=our_message_id,
                                         sent_message_id=wassup_message_id,
                                         delivery_status='delivered')
        elif status == 'failed':
            self.publish_delivery_report(user_message_id=our_message_id,
                                         sent_message_id=wassup_message_id,
                                         delivery_status='failed')
        elif status == 'unsent':
            self.publish_nack(user_message_id=our_message_id,
                              sent_message_id=wassup_message_id,
                              reason=data.get('description'))
        yield self.finish_request(message_id, json.dumps({
            'message_id': message_id
        }))

    @inlineCallbacks
    def handle_inbound_notification(self, message_id, payload, request):
        wassup_uuid = payload['data']['uuid']
        content = payload['data']['content']
        to_addr = payload['data']['to_addr']
        from_addr = payload['data']['from_addr']
        group = payload['data']['group']
        external_id = payload['data']['external_id']
        external_timestamp = payload['data']['external_timestamp']
        yield self.publish_message(
            message_id=message_id,
            content=content,
            group=group,
            to_addr=to_addr,
            from_addr=from_addr,
            transport_type=self.transport_type,
            transport_metadata={
                'wassup': {
                    'message_uuid': wassup_uuid,
                    'external_id': external_id,
                    'external_timestamp': external_timestamp,
                }
            },
        )
        yield self.finish_request(message_id, json.dumps({
            'message_id': message_id
        }))

    @throttle(TPS_LIMIT)
    @inlineCallbacks
    def handle_outbound_message(self, throttle, message):
        # Make sure to relay the available transport
        # metadata back with the outbound message
        tx_metadata = message.get('transport_metadata', {})
        wassup_metadata = tx_metadata.get('wassup', {})
        metadata = {
            'junebug_message_id': message['message_id'],
            'junebug_reply_to': message.get('in_reply_to'),
            'wassup_reply': wassup_metadata,
        }

        http_client = HTTPClient(
            self.agent_factory(self.clock, pool=self.pool))
        resp = yield http_client.post(
            self.get_static_config().api_url,
            data=json.dumps({
                'to_addr': message['to_addr'],
                'number': message['from_addr'],
                'group': message.get('group'),
                'in_reply_to': wassup_metadata.get('message_uuid'),
                'content': message['content'],
                'metadata': metadata,
            }).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Token %s' % (
                    self.get_static_config().token,),
            })
        resp_body = yield resp.json()
        if resp.code != http.CREATED:
            if resp.code == 429:
                self.log.warning('THROTTLING! %s' % (message['content'],))
                yield throttle.manual(self, message)
            else:
                self.log.warning('Unexpected status code: %s, body: %s' % (
                                 resp.code, resp_body))

    def stash(self, func, args, kwargs):
        self.stash_registry[func].append((args, kwargs))

    def get_stashed(self, func):
        return self.stash_registry.pop(func, [])

    def start_throttling(self):
        self.pause_connectors()

    def stop_throttling(self):
        self.unpause_connectors()
