from marathon.exceptions import MarathonError


class MarathonAioHttpError(MarathonError):
    def __init__(self, response, content=None):
        self.error_message = response.reason or ''
        if content:
            self.error_message = content.get('message', self.error_message)
            self.error_details = content.get('details')
        self.status_code = response.status
        super(MarathonAioHttpError, self).__init__(self.__str__())

    def __repr__(self):
        return 'MarathonHttpError: HTTP %s returned with message, "%s"' % \
               (self.status_code, self.error_message)

    def __str__(self):
        return self.__repr__()
