from ably import AblyRest
from ably.rest.channel import Channels
from ably.util.exceptions import AblyAuthException, AblyException
import logging, os, sys
current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_path + '/../')
from data.pubsubservice import PubSubService

class AblyService(PubSubService):
    """ Ably Implementation of Publish Subscriber Service Class """

    def __init__(self, api_key):
        try:
            self._client = AblyRest(api_key)
        except AblyAuthException as exception:
            logging.error("Ably Authentication Exception: %s", str(exception))
            raise exception

    def publish(self, channel_name, event, payload):
        try:
            self._client.channels.get(channel_name).publish(event, payload)
        except AblyException as exception:
            logging.error("""Publish encountered Ably Exception {} with Channel Name:
                             {}, Event: {}, Payload: {}""".format(str(exception),
                                                                  channel_name,
                                                                  event,
                                                                  payload))
            raise exception
