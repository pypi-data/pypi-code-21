from clickatell import Transport

class Http(Transport):
    """
    Provides access to the Clickatell HTTP API
    """

    def __init__(self, apiKey):
        """
        Construct a new API instance with the auth key of the API

        :param str apiKey: The auth key
        """
        self.apiKey = apiKey
        Transport.__init__(self)

    def request(self, action, data={}, headers={}, method='GET'):
        """
        Append the user authentication details to every incoming request
        """
        data = self.merge(data, {'apiKey': self.apiKey})
        return Transport.request(self, action, data, headers, method)

    def sendMessage(self, to, message, extra={}):
        """
        If the 'to' parameter is a single entry, we will parse it into a list.
        We will merge default values into the request data and the extra parameters
        provided by the user.
        """
        to = to if isinstance(to, list) else [to]
        data = {'to': to, 'content': message}
        data = self.merge(data, extra)

        content = self.parseResponse(self.request('messages/http/send', data))

        return content