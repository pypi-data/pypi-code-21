import collections
import copy
import json

from fizzgun.bubbles.utils.bubble_delegate import BubbleDelegate
from fizzgun.models.http_request_builder import HttpRequestBuilder


class JsonVisitor(object):
    """
    Default visitor which produces no transformations (to be extended by actual mutators)
    """
    def visit_key(self, k):
        return k

    def visit_object(self, v):
        return v

    def visit_list(self, v):
        return v

    def visit_string(self, v):
        return v

    def visit_int(self, v):
        return v

    def visit_float(self, v):
        return v

    def visit_null(self, v):
        return v

    def visit_bool(self, v):
        return v

    def visit_list_entry(self, index, value, max_index):
        return index, value


class JsonTraverse(object):
    """
    Goes through every key and value in a json invoking a visitor to generate transformations
    """
    def __init__(self, visitor):
        self.visitor = visitor

    def traverse(self, json_value):
        decoded = json.loads(json_value,
                             object_pairs_hook=collections.OrderedDict)
        for new_value in self._json_transform(decoded):
            yield json.dumps(new_value)

    def _json_transform(self, value):
        if isinstance(value, dict):
            for v in self._dict_transform(value):
                yield v
        elif isinstance(value, list):
            for v in self._list_transform(value):
                yield v
        elif isinstance(value, str):
            yield self.visitor.visit_string(value)
        elif isinstance(value, bool):
            yield self.visitor.visit_bool(value)
        elif isinstance(value, int):
            yield self.visitor.visit_int(value)
        elif isinstance(value, float):
            yield self.visitor.visit_float(value)
        elif value is None:
            yield self.visitor.visit_null(value)

    def _dict_transform(self, value):
        new_obj = self.visitor.visit_object(copy.deepcopy(value))
        if new_obj != value:
            yield new_obj
        for k, v in value.items():
            new_k = self.visitor.visit_key(k)
            # Remove entry transformation
            if new_k is None:
                clone = copy.deepcopy(value)
                clone.pop(k)
                yield clone
            # Change key transformation
            elif not self._same(k, new_k):
                clone = copy.deepcopy(value)
                clone.pop(k)
                clone[new_k] = v
                yield clone
            # Change value transformation
            for new_v in self._json_transform(v):
                if self._same(v, new_v):
                    continue
                clone = copy.deepcopy(value)
                clone[k] = new_v
                yield clone

    def _same(self, v1, v2):
        """
        Specific value comparison
        avoid [True] == [1]
        """
        return v1 == v2 and type(v1) == type(v2) and repr(v1) == repr(v2)

    def _list_transform(self, value):
        new_list = self.visitor.visit_list(copy.deepcopy(value))
        if new_list != value:
            yield new_list
        for i, v in enumerate(value):
            new_i, new_v = self.visitor.visit_list_entry(i, copy.deepcopy(v), len(value) - 1)

            if new_i < 0:  # remove
                new_list = copy.deepcopy(value)
                new_list.pop(i)
                yield new_list
            elif i != min(new_i, len(value) - 1):  # swap
                new_list = copy.deepcopy(value)
                old_val = new_list[new_i]
                new_list[new_i] = new_v
                new_list[i] = old_val
                yield new_list
            elif not self._same(v, new_v):  # just update
                new_list = copy.deepcopy(value)
                new_list[i] = new_v
                yield new_list

            for new_v in self._json_transform(v):
                if self._same(v, new_v):
                    continue
                clone = copy.deepcopy(value)
                clone[i] = new_v
                yield clone


class JsonDelegate(BubbleDelegate):
    """
    Helper class for bubbles dealing with JSON content
    """
    def __init__(self, visitor):
        self._visitor = visitor

    # Override
    def does_apply(self, request):
        return request.content_type_includes('json') and request.has_body()

    # Override
    def generate(self, request):
        for new_json in JsonTraverse(self._visitor).traverse(request.body):
            yield HttpRequestBuilder.new_from(request.value).with_body(new_json).build()
