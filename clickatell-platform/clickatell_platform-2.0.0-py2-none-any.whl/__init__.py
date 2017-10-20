import httplib2
import urllib
import json
import re

class Transport:
    """
    Abstract representation of a transport class. Defines
    the supported API methods
    """

    endpoint = "platform.clickatell.com"

    def __init__(self):
        """
        Construct a new transportation instance.

        :param boolean secure: Should we try and use a secure connection
        """
        pass

    def merge(self, *args):
        """
        Merge multiple dictionary objects into one.

        :param variadic args: Multiple dictionary items

        :return dict
        """
        values = []

        for entry in args:
            values = values + list(entry.items())

        return dict(values)

    def parseResponse(self, response):
        """
        Parse the response from json.
        Remapping error code and messages to be a level higher
        """
        response['body'] = json.loads(response['body'])
        response['messages'] = response['body']['messages']
        response['error'] = response['body']['error']
        del response['body']
        return response

    def request(self, action, data={}, headers={}, method='GET'):
        """
        Run the HTTP request against the Clickatell API

        :param str  action:     The API action
        :param dict data:       The request parameters
        :param dict headers:    The request headers (if any)
        :param str  method:     The HTTP method

        :return: The request response
        """
        http = httplib2.Http()
        body = urllib.urlencode(data)
        url = 'https://' + self.endpoint + '/' + action
        url = (url + '?' + body) if (method == 'GET') else url
        resp, content = http.request(url, method, headers=headers, body=json.dumps(data))
        return self.merge(resp, {'body': content})

    def sendMessage(self, to, message, extra={}):
        """
        Send a message.

        :param list     to:         The number you want to send to (list of strings, or one string)
        :param string   message:    The message you want to send
        :param dict     extra:      Any extra parameters (see Clickatell documentation)

        :return dict
        :raises NotImplementedError
        """
        raise NotImplementedError()