from clickatell import Transport

class Rest(Transport):
    """
    Provides access to the Clickatell REST API
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
        Append the REST headers to every request
        """
        headers = {
            "Authorization": self.apiKey,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        return Transport.request(self, action, data, headers, method)

    def sendMessage(self, to, message, extra={}):
        """
        If the 'to' parameter is a single entry, we will parse it into a list.
        We will merge default values into the request data and the extra parameters
        provided by the user.
        """
        to = to if isinstance(to, list) else [to]
        to = [str(num) for num in to]
        data = {'to': to, 'content': message}
        data = self.merge(data, extra)

        content = self.parseResponse(self.request('messages', data, {}, 'POST'));

        return content