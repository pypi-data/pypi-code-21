from trunity_3_client.utils.url import Url, API_ROOT


base_url = Url(API_ROOT)
base_url.tail = 'topics'


class TopicsDetailClient(object):
    _url = base_url.detail

    def __init__(self, session):
        self._session = session

    def get(self, topic_id):
        """
        :param topic_id:
        :return: {
                  "name": "Chapter 2",
                  "images": [],
                  "image_url": null,
                  "description": "      <html>description</html>"
                }
        """
        url = self._url.format(id=topic_id)
        response = self._session.get(url)
        return response.json()


class TopicsListClient(object):
    _url = base_url.list

    def __init__(self, session):
        self._session = session
        # TODO: add auth from creds
        # TODO: make session auth optional
        # TODO: make code DRY by creating base class

    def post(self, site_id, name, topic_id=None,
             short_name=None, description=None):
        data = {
            'topic[name]': name,
            'topic[short_name]': short_name,
            'topic[description]': description,
            'site_id': site_id,
            'topic_id': topic_id,
        }
        response = self._session.post(self._url, data)
        response.raise_for_status()
        return response.json()['topic_id']


class TopicsClient(object):

    def __init__(self, session):
        self.detail = TopicsDetailClient(session)
        self.list = TopicsListClient(session)
