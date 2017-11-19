import sys

class BaseError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        if sys.version_info > (3,):
            return self.value
        else:
            return unicode(self.value).encode('utf-8')


class KeywordError(BaseError):
    pass
