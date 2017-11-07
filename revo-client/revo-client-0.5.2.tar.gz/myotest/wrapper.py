import dateutil.parser
import json
from datetime import timedelta


class Field(object):

    def __init__(self, source=None):
        self.source = source
        self.client = None

    def convert(self, value, client):
        return value


class StringField(Field):

    def convert(self, value, client):
        if value is None:
            return None
        return str(value)


class BooleanField(Field):

    def convert(self, value, client):
        return True if value else False


class IDField(StringField):
    pass


class FloatField(Field):

    def convert(self, value, client):
        if value is None:
            return None
        return float(value)


class IntegerField(Field):

    def convert(self, value, client):
        if value is None:
            return None
        return int(value)


class DateTimeField(Field):

    def convert(self, value, client):
        if value is None:
            return None
        return dateutil.parser.parse(value)


class DateField(Field):

    def convert(self, value, client):
        if value is None:
            return None
        return dateutil.parser.parse(value).date()


class RawField(Field):

    def convert(self, value, client):
        return value


class DictField(Field):

    def convert(self, value, client):
        if value is None:
            return None
        assert isinstance(value, dict)
        return value


class DurationField(Field):

    def convert(self, value, client):
        if value is None:
            return None
        return timedelta(seconds=float(value))


class DataframeField(Field):

    def convert(self, value, client):
        return value


class LinkField(Field):

    def convert(self, value, client):
        return value


class ListField(Field):

    def __init__(self, subfield: Field, source=None):
        super().__init__(source=source)
        assert subfield is not None
        self.subfield = subfield

    def convert(self, value, client):
        if not value:
            return []
        elif isinstance(value, list):
            return list(map(
                lambda x: self.subfield.convert(x, client),
                value
            ))
        else:
            raise ValueError("Value is not a list, is a {}".format(
                type(value)
            ))


class WrapperObject(Field):

    def __init__(self, client=None, json=None):
        super().__init__()
        if json and not isinstance(json, dict) and not isinstance(json, list):
            raise ValueError("json should nbe a dict or list, got {}".format(
                json
            ))
        self.client = client
        self._json = json
        self._cache = dict()

    def __getattribute__(self, name):
        json = super().__getattribute__("_json")
        cls = super().__getattribute__("__class__")
        cache = super().__getattribute__("_cache")
        client = super().__getattribute__("client")

        if not client:
            return super().__getattribute__(name)

        if name in cache:
            # Cache already contains value
            return cache[name]

        field = getattr(cls, name, None)
        if isinstance(field, Field):
            if name in cache:
                return cache[name]
            json_name = field.source or name
            resolver_fun = getattr(self, "resolve_{}".format(name), None)
            if resolver_fun:
                # we have a resolve function
                orig = resolver_fun(json, field)
            elif isinstance(field, LinkField):
                # Special case to create cyclic references
                return super().__getattribute__(name)
            else:
                orig = json.get(json_name, None)
            if isinstance(orig, WrapperObject):
                # already wrapped
                target = orig
            else:
                target = field.convert(orig, self.client)

            post_resolver_fun = getattr(
                self, "post_resolve_{}".format(name), None)
            if post_resolver_fun:
                new_target = post_resolver_fun(target)
                if new_target is not None:
                    target = new_target

            cache[name] = target
            return target
        else:
            return super().__getattribute__(name)

    def json(self):
        return self._json

    def convert(self, value, client):
        # Duplicate object with filled client and value
        return self.__class__(client, value)

    def __repr__(self):
        if not self.client:
            return "<Prototype: {}>".format(self.__class__)
        else:
            return "<Wrapper [{}]: {}>".format(
                self.__class__,
                json.dumps(self.json(), indent=4))
