from fizzgun.bubbles.utils.json_delegate import JsonDelegate, JsonVisitor
from fizzgun.bubbles.utils.urlencoded_delegate import UrlEncodedDelegate
from fizzgun.bubbles.utils.composite_delegate import BubbleWithDelegates


class Trimmer(BubbleWithDelegates):
    """
    Removes parameters from requests
    """

    TAGS = ['name:trimmer', 'category:data-validation',
            'data:json', 'data:querystring', 'data:x-www-form-urlencoded']

    def initialize(self, json_params=True, urlencoded_params=True, *args, **kwargs):
        super(Trimmer, self).initialize(*args, **kwargs)
        visitor = TrimmerVisitor()
        if json_params:
            self.delegate.add_component(JsonDelegate(visitor))
        if urlencoded_params:
            self.delegate.add_component(UrlEncodedDelegate(visitor))


class TrimmerVisitor(JsonVisitor):
    def visit_key(self, k):
        return None

    def visit_list_entry(self, index, value, max_index):
        return -1, value
