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


class ReadOnly(object):
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
        'error': 'str',
        'status_code': 'int'
    }

    attribute_map = {
        'error': 'error',
        'status_code': 'statusCode'
    }

    def __init__(self, error=None, status_code=None):
        """
        ReadOnly - a model defined in Swagger
        """

        self._error = None
        self._status_code = None

        self.error = error
        self.status_code = status_code

    @property
    def error(self):
        """
        Gets the error of this ReadOnly.
        Given error (not formatted), describes the problem.

        :return: The error of this ReadOnly.
        :rtype: str
        """
        return self._error

    @error.setter
    def error(self, error):
        """
        Sets the error of this ReadOnly.
        Given error (not formatted), describes the problem.

        :param error: The error of this ReadOnly.
        :type: str
        """
        if error is None:
            raise ValueError("Invalid value for `error`, must not be `None`")

        self._error = error

    @property
    def status_code(self):
        """
        Gets the status_code of this ReadOnly.
        Assigned StatusCode, is used in order to create a relationship between Error and Response.

        :return: The status_code of this ReadOnly.
        :rtype: int
        """
        return self._status_code

    @status_code.setter
    def status_code(self, status_code):
        """
        Sets the status_code of this ReadOnly.
        Assigned StatusCode, is used in order to create a relationship between Error and Response.

        :param status_code: The status_code of this ReadOnly.
        :type: int
        """
        if status_code is None:
            raise ValueError("Invalid value for `status_code`, must not be `None`")

        self._status_code = status_code

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
        if not isinstance(other, ReadOnly):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
