"""
Only transverse exceptions must come here. Contextual exceptions must be written in concerned module/package.
"""


class ClientResponseError(Exception):
    def __init__(self, message="Client error", code=None):
        self.message = message
        self.code = code

    def __str__(self):
        return "Error code: %s.\nContent:\n\n%s" % (self.code, self.message)
