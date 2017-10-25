from fizzgun.bubbles.utils.json_delegate import JsonDelegate, JsonVisitor
from fizzgun.bubbles.utils.urlencoded_delegate import UrlEncodedDelegate
from fizzgun.bubbles.utils.composite_delegate import BubbleWithDelegates


class Enlarger(BubbleWithDelegates):
    """
    Identifies parameters in requests and replaces them with larger values
    """

    TAGS = ['name:enlarger', 'category:data-validation',
            'data:json', 'data:querystring', 'data:x-www-form-urlencoded']

    def initialize(self, grow_factor=1000, grow_keys=False, json_params=True, urlencoded_params=True, *args, **kwargs):
        super(Enlarger, self).initialize(*args, **kwargs)
        visitor = EnlargerVisitor(grow_factor, grow_keys)
        if json_params:
            self.delegate.add_component(JsonDelegate(visitor))
        if urlencoded_params:
            self.delegate.add_component(UrlEncodedDelegate(visitor))


class EnlargerVisitor(JsonVisitor):
    def __init__(self, grow_factor, grow_keys):
        self._factor = grow_factor
        self._grow_keys = grow_keys

    def visit_key(self, k):
        if self._grow_keys:
            return k * self._factor
        return k

    def visit_list(self, v):
        return v * self._factor

    def visit_string(self, v):
        v = v or 'a'
        return v * self._factor

    def visit_int(self, v):
        if -1 <= v <= 1:
            v = 123 * self._sign(v)
        return v ** self._factor

    def visit_float(self, v):
        if -1 <= v <= 1:
            v = 123.0 * self._sign(v)
        return v ** self._factor

    def _sign(self, number):
        return (1, -1)[number < 0]
