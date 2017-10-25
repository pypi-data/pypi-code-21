from fizzgun.bubbles.utils.json_delegate import JsonDelegate, JsonVisitor
from fizzgun.bubbles.utils.composite_delegate import BubbleWithDelegates


class TypeChanger(BubbleWithDelegates):
    """
    Changes parameter values with others of a different type
    """

    TAGS = ['name:type-changer', 'category:data-validation', 'data:json']

    def initialize(self, json_params=True, type_samples=None, *args, **kwargs):
        super(TypeChanger, self).initialize(*args, **kwargs)
        if json_params:
            self.delegate.add_component(JsonDelegate(TypeChangerVisitor(type_samples, self._random_generator)))


class TypeChangerVisitor(JsonVisitor):
    def __init__(self, type_samples, random_generator):
        self._random_generator = random_generator
        self._sample = type_samples or {
            'object': {'fizz': 'gun'},
            'list': [1, 'FizzGun', 3],
            'null': None,
            'string': 'FiZzGuN',
            'int': 42,
            'float': 3.1415926,
            'bool': True
        }
        self._types = sorted(self._sample.keys())

    def visit_object(self, v):
        return self._different_than('object')

    def visit_list(self, v):
        return self._different_than('list')

    def visit_string(self, v):
        return self._different_than('string')

    def visit_int(self, v):
        return self._different_than('int')

    def visit_float(self, v):
        return self._different_than('int', 'float')

    def visit_null(self, v):
        return self._different_than('null')

    def visit_bool(self, v):
        return self._different_than('bool')

    def _different_than(self, *type_names):
        new_type = self._random_generator.choice([k for k in self._types if k not in type_names])
        return self._sample[new_type]
