from trunity_3_client.utils.url import Url, API_ROOT


base_url = Url(API_ROOT)
base_url.tail = 'contents'


class ContentsDetailClient(object):
    _url = base_url.detail

    def __init__(self, session):
        self._session = session

    def get(self, content_id):
        """

        :param content_id:
        :return: {
                  "name": "asdfasdf",
                  "description": "      <html> ... </html>",
                  "image_url": null,
                  "images": []
                }
        """
        url = self._url.format(id=content_id)
        response = self._session.get(url)
        return response.json()


class ContentType:
    ARTICLE = 'article'
    QUESTIONNAIRE = 'questionnaire'

    _CHOICES = (
        ARTICLE,
        QUESTIONNAIRE,
    )


class ResourceType:
    QUESTION_POOL = 0
    SELF_ASSESSMENTS = 1
    TEST = 2
    FLASH_CARDS = 3

    _CHOICES = (
        QUESTION_POOL,
        SELF_ASSESSMENTS,
        TEST,
        FLASH_CARDS,
    )


class ContentTypeError(ValueError):
    pass


class ResourceTypeError(ValueError):
    pass


class ContentsListClient(object):
    _url = base_url.list

    def __init__(self, session):
        self._session = session

    @staticmethod
    def _check_content_type(value):
        choices = ContentType._CHOICES

        if value not in choices:
            raise ContentTypeError(
                "content_type must be on of {}".format(str(choices))
            )

    @staticmethod
    def _check_resource_type(value):
        choices = ResourceType._CHOICES

        if value not in choices:
            raise ResourceTypeError(
                "content_type must be on of {}".format(str(choices))
            )

    def post(self, site_id, content_title, content_type,
             topic_id=None, resource_type=None, text=None, short_text=None):

        self._check_content_type(content_type)

        if content_type == 'questionnaire':
            self._check_resource_type(resource_type)

        data = {
            'content_type': content_type,
            'content[title]': content_title,
            'site_id': site_id,
            'topic_id': topic_id,
            'content[resource_type]': resource_type,
            'content[text]': text,
            'content[short_text]': short_text,

        }
        response = self._session.post(self._url, data)
        response.raise_for_status()
        return response.json()['content_id']


class ContentsClient(object):

    def __init__(self, session):
        self.detail = ContentsDetailClient(session)
        self.list = ContentsListClient(session)