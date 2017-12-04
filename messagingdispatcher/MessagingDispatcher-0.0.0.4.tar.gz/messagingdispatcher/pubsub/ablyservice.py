import base64, json, logging, os, requests, sys
current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_path + '/../')
from messagingdispatcher.pubsub.pubsubservice import PubSubService

class AblyService(PubSubService):
    """ Ably Implementation of Publish Subscriber Service Class """

    def __init__(self, api_key):
        self._api_key = api_key

    def publish(self, channel_name, event, payload):
        try:
            authorization_value = base64.b64encode(self._api_key.encode()).decode("utf-8")
            requests.post('https://rest.ably.io/channels/{}/messages'.format(channel_name), 
                          data=json.dumps({'name': event, 'data': payload}),
                          headers={"content-type":"application/json", "Authorization":"Basic {}".format(authorization_value) })
        except Exception as exception:
            logging.error("""Publish encountered Ably Exception {} with Channel Name:
                             {}, Event: {}, Payload: {}""".format(str(exception),
                                                                  channel_name,
                                                                  event,
                                                                  payload))
            raise exception
