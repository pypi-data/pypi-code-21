from flask import Response
import json
import pickle

class ResponseHandler(Response):
    def __init__(self, content = None, *args, **kwargs):
        """
        Serialize content of the response
        """
        for item in content:
            if isinstance(item, set):
                item = list(item)
            for i in item:
                if isinstance(item[i], set):
                    item[i] = list(item[i])
        super(Response, self).__init__(json.dumps(content), *args, **kwargs)

    @classmethod
    def force_type(cls, rv, environ=None):
        if isinstance(rv, (dict, list)):
            return cls(rv)

        return super(ResponseHandler, cls).force_type(rv, environ)
