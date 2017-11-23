from flask import Response
import json

class ResponseHandler(Response):
    def __init__(self, content = None, *args, **kwargs):
        """
        Serialize content of the response
        """
        super(Response, self).__init__(content, *args, **kwargs)

    @classmethod
    def force_type(cls, rv, environ=None):
        if isinstance(rv, (dict, list)):
            return cls(rv)

        return super(ResponseHandler, cls).force_type(rv, environ)
