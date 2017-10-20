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


class StoryRelations(object):
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
        'tags': 'StoryRelationsTags',
        'items': 'StoryRelationsItems',
        'model_type': 'BroadcastRelationsModelType'
    }

    attribute_map = {
        'tags': 'tags',
        'items': 'items',
        'model_type': 'model_type'
    }

    def __init__(self, tags=None, items=None, model_type=None):
        """
        StoryRelations - a model defined in Swagger
        """

        self._tags = None
        self._items = None
        self._model_type = None

        if tags is not None:
          self.tags = tags
        if items is not None:
          self.items = items
        if model_type is not None:
          self.model_type = model_type

    @property
    def tags(self):
        """
        Gets the tags of this StoryRelations.

        :return: The tags of this StoryRelations.
        :rtype: StoryRelationsTags
        """
        return self._tags

    @tags.setter
    def tags(self, tags):
        """
        Sets the tags of this StoryRelations.

        :param tags: The tags of this StoryRelations.
        :type: StoryRelationsTags
        """

        self._tags = tags

    @property
    def items(self):
        """
        Gets the items of this StoryRelations.

        :return: The items of this StoryRelations.
        :rtype: StoryRelationsItems
        """
        return self._items

    @items.setter
    def items(self, items):
        """
        Sets the items of this StoryRelations.

        :param items: The items of this StoryRelations.
        :type: StoryRelationsItems
        """

        self._items = items

    @property
    def model_type(self):
        """
        Gets the model_type of this StoryRelations.

        :return: The model_type of this StoryRelations.
        :rtype: BroadcastRelationsModelType
        """
        return self._model_type

    @model_type.setter
    def model_type(self, model_type):
        """
        Sets the model_type of this StoryRelations.

        :param model_type: The model_type of this StoryRelations.
        :type: BroadcastRelationsModelType
        """

        self._model_type = model_type

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
        if not isinstance(other, StoryRelations):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
