

class Producer(object):
    """
    The starting entity of the Fizzgun stack.
    Receives requests from a request source, transform them to fizzgun format, decides if the
    request applies for fuzzing and if so forwards it to the next entity in the chain
    """
    def __init__(self, source_adapter, output):
        self._adapter = source_adapter
        self._output = output

    def produce(self, obj, session_id=None):
        request = self._adapter.convert(obj)

        self._output.push({'original': request, 'session_id': session_id})


class SourceAdapter(object):
    """
    Interface-like object. Transform request representations from different sources into
    the representation that Fizzgun can handle.
    """
    FIELDS = ['method', 'scheme', 'host', 'port', 'path', 'query', 'http_version', 'headers', 'body']

    def convert(self, request_obj):
        raise NotImplementedError("'convert' must be implemented in class '%s'" % self.__class__.__name__)
