# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = "the01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017, Florian JUNG"
__license__ = "MIT"
__version__ = "0.1.0"
__date__ = "2017-11-03"
# Created: 2017-10-06 23:35


class CacheInfo(object):
    """ Cache information """

    def __init__(self, access_time=None, etag = None):
        super(CacheInfo, self).__init__()
        self.etag = etag
        """ :type : None | str | unicode """
        self.access_time = access_time
        """ :type : None | datetime.datetime """

    def __repr__(self):
        return "<CacheInfo ({}, {})>".format(
            self.access_time, self.etag
        )

    def __str__(self):
        return "{}, {}".format(self.access_time, self.etag)

    def __unicode__(self):
        return self.__str__()

    def to_dict(self):
        """
        CacheInfo as dict

        :return: cache info
        :rtype: dict
        """
        return {
            'access_time': self.access_time,
            'etag': self.etag
        }

    @staticmethod
    def from_dict(d):
        """
        CacheInfo from dict

        :param d: Dict to load
        :type d: dict
        :return: cache info
        :rtype: CacheInfo
        """
        if d is None:
            return None
        return CacheInfo(
            d.get('access_time'),
            d.get('etag')
        )


class Response(object):
    """ Scrapper response object """

    def __init__(self, html=None, cache_info=None, scraped=None, raw=None):
        super(Response, self).__init__()
        self.cache_info = cache_info
        """ :type : None | CacheInfo """
        self.raw = raw
        """ Raw, undecoded reponse
            :type : None | unicode """
        self.html = html
        """ Html reponse
            :type : None | unicode """
        self.scraped = scraped
        """ Scrapped content
            :type : None | list | dict """

    def __repr__(self):
        return "<Response ({}, {}, {}, {})>".format(
            self.cache_info, self.html, self.scraped, self.raw
        )

    def __str__(self):
        return "({}), {}, {}, {}".format(
            self.cache_info, self.html, self.scraped, self.raw
        )

    def __unicode__(self):
        return self.__str__()

    def to_dict(self):
        """
        Response as dict

        :return: response
        :rtype: dict
        """
        cache_info = None
        if self.cache_info:
            cache_info = self.cache_info.to_dict()
        return {
            'cache_info': cache_info,
            'html': self.html,
            'scraped': self.scraped,
            'raw': self.raw
        }

    @staticmethod
    def from_dict(d):
        """
        Response from dict

        :param d: Dict to load
        :type d: dict
        :return: response
        :rtype: Response
        """
        if d is None:
            return None
        return Response(
            d.get('html'),
            CacheInfo.from_dict(d.get('cache_info')),
            d.get('scraped'),
            d.get('raw')
        )
