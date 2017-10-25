from fizzgun.bubbles.utils.json_delegate import JsonDelegate, JsonVisitor
from fizzgun.bubbles.utils.urlencoded_delegate import UrlEncodedDelegate
from fizzgun.bubbles.utils.composite_delegate import BubbleWithDelegates


class Injector(BubbleWithDelegates):
    """
    Identifies parameters in requests and attempts to find errors by injecting special sequences
    """

    TAGS = ['name:injector', 'category:security',
            'data:json', 'data:querystring', 'data:x-www-form-urlencoded']

    def initialize(self, json_params=True, urlencoded_params=True, *args, **kwargs):
        super(Injector, self).initialize(*args, **kwargs)
        visitor = InjectorVisitor()
        if json_params:
            self.delegate.add_component(JsonDelegate(visitor))
        if urlencoded_params:
            self.delegate.add_component(UrlEncodedDelegate(visitor))


class InjectorVisitor(JsonVisitor):

    def visit_string(self, v):
        return v + "'`t;--/*"
