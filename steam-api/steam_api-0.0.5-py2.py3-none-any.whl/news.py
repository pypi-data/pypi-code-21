from .api.news import get_news_for_app
from .error import ParameterRequiredError


class News(object):
    """
    Steam News Service

    .. note::
       https://developer.valvesoftware.com/wiki/Steam_Web_API#GetNewsForApp_.28v0002.29

    Example 1:

    .. code-block:: python

       # initialize News object with `app_id`
       import steam_api

       news = steam_api.news.News(440)

       # list news items from property
       news.news_items

    Example 2:

    .. code-block:: python

       # initialize News object without `app_id`
       import steam_api
       from steam_api.error import ParameterRequiredError

       try:
         steam_api.news.News()
       except: ParameterRequiredError
          # catch error

    Example 3:

    .. code-block:: python

       # initialize News object with a non-exist `app_id`, try 0
       import steam_api
       from steam_api.error import *

       try:
           steam_api.news.News(0)
       except SteamAPIFailureForbidden:
           # catch error
    """

    def __init__(self, app_id=None, limit=20, count=0, max_length=300):
        """
        initialize News

        :param app_id: steam app id
        :param limit: set limit of list, default 20
        :param count: count
        :param max_length: set max length of content, default 300

        :raises ParameterRequiredError: if the `app_id` is not provided

        """
        if app_id is None:
            raise ParameterRequiredError('app_id can not be empty')

        #: app id
        self.app_id = app_id

        #: news items count
        self.count = count

        #: size of returned news items list
        self.limit = limit

        #: max length of item content
        self.max_length = max_length

    @property
    def news_items(self):
        """
        gets the news list

        Sample

        .. code-block:: javascript

            [
            {gid: "2140760316587859925",
            title: "Team Fortress 2 Update Released",
            url: "http://store.steampowered.com/news/externalpost/tf2_blog/2140760316587859925",
            is_external_url: true,
            author: "",
            contents: "An update to Team Fortress 2 has been released.cally w...",
            feedlabel: "TF2 Blog",
            date: 1509579120,
            feedname: "tf2_blog",
            feed_type: 0,
            appid: 440
            }, {}, {}, ...
            ]

        :return: List
        """
        res = get_news_for_app(self.app_id, self.limit, self.max_length)
        news = res['appnews']
        self.app_id = news['appid']
        self.count = news['count']

        return news['newsitems']