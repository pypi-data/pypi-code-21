class TeampassHttpException(Exception):
    def __init__(self, http_code, msg=None):
        self.msg = msg
        self.http_code = http_code

    def __str__(self):
        return u"HTTP CODE: {}, Error: {}".format(self.http_code, self.msg)

    def __unicode__(self):
        return u"HTTP CODE: {}, Error: {}".format(self.http_code, self.msg)


class TeampassApiException(Exception):
    def __init__(self, msg=None):
        self.msg = msg

    def __str__(self):
        return u"Error: {}".format(self.msg)

    def __unicode__(self):
        return u"Error: {}".format(self.msg)
