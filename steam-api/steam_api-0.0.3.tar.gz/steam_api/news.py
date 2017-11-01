from .api import SteamApiRequest, NEWS_ENDPOINT


# API call
def get_news_for_app(app_id=None, count=None, max_length=None, format='json'):
    """
    GetNewsForApp returns the latest of a game specified by its appID.

    :param app_id: AppID of the game you want the news of. Required
    :param count: How many news entries you want to get returned. default seems to be 20
      BUT if you pass count value 1. It will return the number of whole items.
    :param max_length: Maximum length of each news entry.
    :param format: Output format. json (default), xml or vdf.
    :return:
    """

    payload = {
        'appid': app_id,
        'count': count,
        'maxlength': max_length,
        'format': format,
    }

    return SteamApiRequest.get(
        NEWS_ENDPOINT, '/GetNewsForApp', 'v0002', payload)


class News(object):
    def __init__(self, app_id=None, limit=20, count=0, max_length=300):
        if app_id is None:
            raise ValueError('app_id can not be empty')

        self.app_id = app_id
        self.count = count
        self.limit = limit
        self.max_length = max_length

    @property
    def news_items(self):
        try:
            res = get_news_for_app(self.app_id, self.limit, self.max_length)
            news = res['appnews']
            self.app_id = news['appid']
            self.count = news['count']

            return news['newsitems']

        except ValueError:
            return []


