""" Exception classes """


class BotChuckyTokenError(Exception):
    def __init__(self, api_name):
        """
        :param api_name: Api Name to show error for
        """
        self._api_name = api_name

    def __str__(self):
        return 'Seems like you missing add'\
               ' {0} token to the ChuckyBot class'.format(self._api_name)


class BotChuckyInvalidToken(Exception):
    pass


class BotChuckyError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg
