from trunity_3_client.utils.url import Url, API_ROOT


base_url = Url(API_ROOT)
base_url.tail = 'sites'


class SiteType:
    TEXTBOOK = 'Textbook'
    COURSE = 'Course'
    COLLECTION = 'Collection'

    _CHOICES = (
        TEXTBOOK,
        COURSE,
        COLLECTION,
    )


class SiteTypeError(ValueError):
    pass


class SitesListClient(object):
    _url = base_url.list

    def __init__(self, session):
        self._session = session

    @staticmethod
    def _validate_site_type(site_type):
        if site_type not in SiteType._CHOICES:
            raise SiteTypeError(
                "site_type must be one of {}".format(SiteType._CHOICES)
            )

    def post(self, name: str, site_type: str, description) -> int:
        """
        Create site

        :return: site_id
        """

        self._validate_site_type(site_type)

        data = {
            'site[name]': name,
            'site[type]': site_type,
            'site[description]': description,
        }
        response = self._session.post(self._url, data)
        response.raise_for_status()
        return response.json()['site_id']

    def get(self):
        """
        Return list of available to the user sites.

        :return: list of sites.

        Example:
        {
          "id": 165,
          "name": "New course. Level 19",
          "type": "Course",
          "image_url": "/uploads/topic/image/304/OH9A1152_zpsvrp7jxs9.jpg"
        },
        """
        response = self._session.get(self._url)
        response.raise_for_status()
        return response.json()['sites']


class SitesClient(object):

    def __init__(self, session):
        self.list = SitesListClient(session)

