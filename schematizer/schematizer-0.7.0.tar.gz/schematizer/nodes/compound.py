from schematizer.exceptions import (
    BaseValidationError, CompoundValidationError, NestedValidationError, SimpleValidationError,
    StopValidation,
)
from schematizer.nodes.base import BaseCoercibleNode, BaseNode


def _force_key(str_or_key, **kwargs):
    if isinstance(str_or_key, Key):
        return str_or_key
    else:
        return Key(str_or_key, **kwargs)


class Key:
    def __init__(self, primitive, native=None, required=True):
        self.primitive = primitive
        self.native = native or primitive
        self.required = required

    def __hash__(self):
        return hash(self.primitive)


class ListNode(BaseCoercibleNode):
    coerce_primitive = list

    def __init__(self, node):
        super().__init__()
        self.node = node

    def to_native(self, obj):
        obj = super().to_native(obj)
        result = []
        errors = []
        for i, item in enumerate(obj):
            try:
                result.append(self.node.to_native(item))
            except BaseValidationError as exc:
                errors.append(NestedValidationError(i, exc))
        if errors:
            raise CompoundValidationError(errors)
        else:
            return result

    def to_primitive(self, obj):
        return [self.node.to_primitive(item) for item in obj]


class BaseEntityNode(BaseCoercibleNode):
    coerce_primitive = dict

    def __init__(self, nodes, **kwargs):
        super().__init__()
        self.nodes = {
            _force_key(str_or_key, **kwargs): node
            for str_or_key, node in nodes.items()
        }

    def get_prop(self, obj, key):
        raise NotImplementedError

    def extended(self, nodes, **kwargs):
        return self.__class__({**self.nodes, **nodes}, **kwargs)

    def to_native(self, obj):
        obj = super().to_native(obj)
        result = {}
        errors = []
        for key, node in self.nodes.items():
            try:
                prop = obj[key.primitive]
            except KeyError:
                if key.required:
                    error = NestedValidationError(
                        key.primitive, SimpleValidationError('MISSING'),
                    )
                    errors.append(error)
                continue
            try:
                result[key.native] = node.to_native(prop)
            except BaseValidationError as exc:
                errors.append(
                    NestedValidationError(key.primitive, exc),
                )
        if errors:
            raise CompoundValidationError(errors)
        else:
            return result

    def to_primitive(self, obj):
        result = {}
        for key, node in self.nodes.items():
            prop = self.get_prop(obj, key.native)
            result[key.primitive] = node.to_primitive(prop)
        return result


class DictNode(BaseEntityNode):
    def get_prop(self, obj, key):
        return obj[key]


class ObjectNode(BaseEntityNode):
    def get_prop(self, obj, key):
        return getattr(obj, key)


class CalledNode(BaseNode):
    def __init__(self, node, *args, **kwargs):
        self.node = node
        self.args = args
        self.kwargs = kwargs

    def to_primitive(self, obj):
        return self.node.to_primitive(
            obj(*self.args, **self.kwargs),
        )


class WrappedNode(BaseNode):
    def __init__(self, node, validators):
        super().__init__()
        self.node = node
        self.validators = validators

    def to_native(self, obj):
        try:
            for validator in self.validators:
                validator.validate_primitive(obj)
        except StopValidation:
            return obj
        obj = self.node.to_native(obj)
        for validator in self.validators:
            validator.validate_native(obj)
        return obj

    def to_primitive(self, obj):
        try:
            for validator in self.validators:
                validator.validate_native(obj)
        except StopValidation:
            return obj
        obj = self.node.to_primitive(obj)
        for validator in self.validators:
            validator.validate_primitive(obj)
        return obj


List = ListNode
Dict = DictNode
Object = ObjectNode
Called = CalledNode
Wrapped = WrappedNode
