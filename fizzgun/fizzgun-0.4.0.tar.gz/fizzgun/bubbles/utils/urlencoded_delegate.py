import copy
import urllib.parse

import fizzgun.util
from fizzgun.models import HttpRequest, HttpRequestBuilder
from fizzgun.bubbles.utils.bubble_delegate import BubbleDelegate


class FormUrlEncodedVisitor(object):
    """
    Default visitor which produces no transformations (to be extended by actual mutators)
    """
    def visit_key(self, k):
        return k

    def visit_string(self, v):
        return v


class FormUrlEncodedTraverse(object):
    """
    Goes through every key and value in a urlencoded param string invoking a visitor to generate transformations
    """
    def __init__(self, visitor):
        self.visitor = visitor

    def traverse(self, value):
        params = fizzgun.util.parse_qs(value, keep_blank_values=True)

        for new_params in self._urlencoded_params_transform(params):
            yield urllib.parse.urlencode(new_params, doseq=True)

    def _urlencoded_params_transform(self, value):
        for k, v in value.items():
            new_k = self.visitor.visit_key(k)
            # Remove entry transformation
            if new_k is None:
                clone = copy.deepcopy(value)
                clone.pop(k)
                yield clone
            # Change key transformation
            elif new_k != k:
                clone = copy.deepcopy(value)
                clone.pop(k)
                clone[new_k] = v
                yield clone

            # Change value transformation
            for index, item in enumerate(v):
                new_item = self.visitor.visit_string(item)
                if new_item == item:
                    continue
                if new_item is None:  # remove
                    new_v = copy.deepcopy(v)
                    del new_v[index]
                    clone = copy.deepcopy(value)
                    clone[k] = new_v
                    yield clone
                else:  # modify
                    new_v = copy.deepcopy(v)
                    new_v[index] = new_item
                    clone = copy.deepcopy(value)
                    clone[k] = new_v
                    yield clone


class UrlEncodedDelegate(BubbleDelegate):
    """
    Abstract class for bubbles dealing with urlencoded arguments
    either in query strings or body
    """
    def __init__(self, visitor):
        self._visitor = visitor

    # Override
    def does_apply(self, request: HttpRequest):
        return self.has_urlencoded_body(request) or self.has_querystring(request)

    # Override
    def generate(self, request: HttpRequest):
        if self.has_querystring(request):
            for new_query in FormUrlEncodedTraverse(self._visitor).traverse(request.query):
                yield HttpRequestBuilder.new_from(request.value).with_query(new_query).build()
        if self.has_urlencoded_body(request):
            for new_body in FormUrlEncodedTraverse(self._visitor).traverse(request.body):
                yield HttpRequestBuilder.new_from(request.value).with_body(new_body).build()

    def has_querystring(self, request: HttpRequest):
        return request.query

    def has_urlencoded_body(self, request: HttpRequest):
        return request.content_type_includes('application/x-www-form-urlencoded') and request.has_body()
