# coding: utf-8

"""
    RadioManager

    RadioManager

    OpenAPI spec version: 2.0
    Contact: support@pluxbox.com
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from pprint import pformat
from six import iteritems
import re


class StoryResults(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'current_page': 'int',
        '_from': 'int',
        'last_page': 'int',
        'next_page_url': 'str',
        'path': 'str',
        'per_page': 'int',
        'prev_page_url': 'str',
        'to': 'int',
        'total': 'int',
        'results': 'list[StoryResult]'
    }

    attribute_map = {
        'current_page': 'current_page',
        '_from': 'from',
        'last_page': 'last_page',
        'next_page_url': 'next_page_url',
        'path': 'path',
        'per_page': 'per_page',
        'prev_page_url': 'prev_page_url',
        'to': 'to',
        'total': 'total',
        'results': 'results'
    }

    def __init__(self, current_page=None, _from=None, last_page=None, next_page_url=None, path=None, per_page=None, prev_page_url=None, to=None, total=None, results=None):
        """
        StoryResults - a model defined in Swagger
        """

        self._current_page = None
        self.__from = None
        self._last_page = None
        self._next_page_url = None
        self._path = None
        self._per_page = None
        self._prev_page_url = None
        self._to = None
        self._total = None
        self._results = None

        if current_page is not None:
          self.current_page = current_page
        if _from is not None:
          self._from = _from
        if last_page is not None:
          self.last_page = last_page
        if next_page_url is not None:
          self.next_page_url = next_page_url
        if path is not None:
          self.path = path
        if per_page is not None:
          self.per_page = per_page
        if prev_page_url is not None:
          self.prev_page_url = prev_page_url
        if to is not None:
          self.to = to
        if total is not None:
          self.total = total
        if results is not None:
          self.results = results

    @property
    def current_page(self):
        """
        Gets the current_page of this StoryResults.

        :return: The current_page of this StoryResults.
        :rtype: int
        """
        return self._current_page

    @current_page.setter
    def current_page(self, current_page):
        """
        Sets the current_page of this StoryResults.

        :param current_page: The current_page of this StoryResults.
        :type: int
        """

        self._current_page = current_page

    @property
    def _from(self):
        """
        Gets the _from of this StoryResults.

        :return: The _from of this StoryResults.
        :rtype: int
        """
        return self.__from

    @_from.setter
    def _from(self, _from):
        """
        Sets the _from of this StoryResults.

        :param _from: The _from of this StoryResults.
        :type: int
        """

        self.__from = _from

    @property
    def last_page(self):
        """
        Gets the last_page of this StoryResults.

        :return: The last_page of this StoryResults.
        :rtype: int
        """
        return self._last_page

    @last_page.setter
    def last_page(self, last_page):
        """
        Sets the last_page of this StoryResults.

        :param last_page: The last_page of this StoryResults.
        :type: int
        """

        self._last_page = last_page

    @property
    def next_page_url(self):
        """
        Gets the next_page_url of this StoryResults.

        :return: The next_page_url of this StoryResults.
        :rtype: str
        """
        return self._next_page_url

    @next_page_url.setter
    def next_page_url(self, next_page_url):
        """
        Sets the next_page_url of this StoryResults.

        :param next_page_url: The next_page_url of this StoryResults.
        :type: str
        """

        self._next_page_url = next_page_url

    @property
    def path(self):
        """
        Gets the path of this StoryResults.

        :return: The path of this StoryResults.
        :rtype: str
        """
        return self._path

    @path.setter
    def path(self, path):
        """
        Sets the path of this StoryResults.

        :param path: The path of this StoryResults.
        :type: str
        """

        self._path = path

    @property
    def per_page(self):
        """
        Gets the per_page of this StoryResults.

        :return: The per_page of this StoryResults.
        :rtype: int
        """
        return self._per_page

    @per_page.setter
    def per_page(self, per_page):
        """
        Sets the per_page of this StoryResults.

        :param per_page: The per_page of this StoryResults.
        :type: int
        """

        self._per_page = per_page

    @property
    def prev_page_url(self):
        """
        Gets the prev_page_url of this StoryResults.

        :return: The prev_page_url of this StoryResults.
        :rtype: str
        """
        return self._prev_page_url

    @prev_page_url.setter
    def prev_page_url(self, prev_page_url):
        """
        Sets the prev_page_url of this StoryResults.

        :param prev_page_url: The prev_page_url of this StoryResults.
        :type: str
        """

        self._prev_page_url = prev_page_url

    @property
    def to(self):
        """
        Gets the to of this StoryResults.

        :return: The to of this StoryResults.
        :rtype: int
        """
        return self._to

    @to.setter
    def to(self, to):
        """
        Sets the to of this StoryResults.

        :param to: The to of this StoryResults.
        :type: int
        """

        self._to = to

    @property
    def total(self):
        """
        Gets the total of this StoryResults.

        :return: The total of this StoryResults.
        :rtype: int
        """
        return self._total

    @total.setter
    def total(self, total):
        """
        Sets the total of this StoryResults.

        :param total: The total of this StoryResults.
        :type: int
        """

        self._total = total

    @property
    def results(self):
        """
        Gets the results of this StoryResults.

        :return: The results of this StoryResults.
        :rtype: list[StoryResult]
        """
        return self._results

    @results.setter
    def results(self, results):
        """
        Sets the results of this StoryResults.

        :param results: The results of this StoryResults.
        :type: list[StoryResult]
        """

        self._results = results

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """
        Returns the string representation of the model
        """
        return pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        if not isinstance(other, StoryResults):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
