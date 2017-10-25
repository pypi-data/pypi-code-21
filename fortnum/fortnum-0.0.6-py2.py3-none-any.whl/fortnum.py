from collections import OrderedDict, Sized
from weakref import WeakKeyDictionary

from fortnum.utils import OrderedSet, RelatedFortnums


class FortnumException(Exception):
    pass


class DuplicatedFortnum(FortnumException):
    pass


class FortnumDoesNotExist(FortnumException):
    pass


class MultipleParents(FortnumException):
    pass


class UnableToAddRelatedFortnum(FortnumException):
    pass


class class_property(classmethod):
    def __get__(self, instance, owner):
        return super().__get__(instance, owner)()


class FortnumMeta(type):
    _registry = {}

    @classmethod
    def __prepare__(mcs, name, bases):
        return OrderedDict()

    def __new__(mcs, name, bases, classdict):
        if name in mcs._registry:
            raise DuplicatedFortnum()

        # Create Fortnum class and add to registry
        fortnum = type.__new__(mcs, name, bases, dict(classdict))
        mcs._registry[name] = fortnum

        # Initialize fortnum attributes
        fortnum.parent = None
        fortnum.parents = OrderedSet()
        fortnum.parent_index = {}
        fortnum.children = OrderedDict()

        # Identify children and register parent connections
        item_class = fortnum.item_class
        related_name = fortnum.related_name
        for key, value in classdict.items():
            if issubclass(type(value), FortnumMeta):
                # Create related fortnum sets
                if related_name:
                    related_fortnums = getattr(value, related_name, None)
                    if related_fortnums is None:
                        related_fortnums = RelatedFortnums()
                    elif not isinstance(related_fortnums, RelatedFortnums):
                        raise UnableToAddRelatedFortnum(
                            "Unable to add related fortnums to '%s' attribute '%s' it would override the value '%s'." %
                            (value, related_name, related_fortnums)
                        )
                    related_fortnums.add(fortnum)
                    setattr(value, related_name, related_fortnums)

                # Add children
                if item_class and not issubclass(value, item_class) or key == "item_class":
                    continue
                fortnum.children[key] = value

        for index, child in enumerate(fortnum.children.values()):
            if child.parent is None:
                child.parent = fortnum
            child.parents.add(fortnum)
            child.parent_index[fortnum] = index

        return fortnum

    def __iter__(self):
        for fortnum in self.children.values():
            yield fortnum

    def __getitem__(self, item):
        return self.children.__getitem__(item)

    def __len__(self):
        return len(self.children)

    def __bool__(self):
        return True

    def __str__(self):
        return self.__name__

    def __repr__(self):
        return str(self)

    @property
    def choices(self):
        return ((str(item), str(item)) for item in self.__iter__())

    def common_parent(self, other):
        if not issubclass(other, Fortnum):
            return TypeError("Fortnums can only be compared with other fortnums. other is of type '%s'" % type(other))

        try:
            return next(iter(self.parents & other.parents))

        except StopIteration:
            raise TypeError("Only fortnums with atleast one common parent can be compared.")

    def __gt__(self, other):
        parent = self.common_parent(other)
        return self.parent_index[parent].__gt__(other.parent_index[parent])

    def __lt__(self, other):
        parent = self.common_parent(other)
        return self.parent_index[parent].__lt__(other.parent_index[parent])


def serialize_fortnum(fortnum):
    return fortnum.__name__


def deserialize_fortnum(name):
    try:
        return FortnumMeta._registry[name]
    except KeyError:
        raise FortnumDoesNotExist()


class Fortnum(metaclass=FortnumMeta):
    parent = None  # Set by Metaclass
    parents = None  # Set by Metaclass
    children = None  # Set by Metaclass
    parent_index = None  # Set by Metaclass
    item_class = None
    related_name = None

    def __new__(cls, name, **kwargs):
        # Allow fetching of already defined fortnums.
        try:
            return deserialize_fortnum(name)
        except FortnumDoesNotExist:
            return FortnumMeta(name, (cls,), kwargs)

    @classmethod
    def serialize(cls):
        return serialize_fortnum(cls)

    @classmethod
    def deserialize(cls, name):
        fortnum = deserialize_fortnum(name)
        if fortnum not in cls:
            raise FortnumDoesNotExist("'%s' is not a valid option for '%s'. Try %s" % (
                name,
                cls,
                list(cls)
            ))
        return fortnum

    @class_property
    def subclasses(cls):
        return cls.__subclasses__()

    @class_property
    def parent(cls):
        if not cls.parents:
            return None

        if len(cls.parents) == 1:
            return cls.parents[0]

        raise MultipleParents

    @classmethod
    def descendants(cls, include_self=False):
        if include_self:
            yield cls

        for child in cls:
            yield child

            for descendant in child.descendants():
                yield descendant

    @classmethod
    def root(cls):
        root = cls
        while root.parent:
            root = root.parent
        return root

    @classmethod
    def ancestors(cls, ascending=False, include_self=False):
        ancestors = []
        if include_self:
            ancestors.append(cls)
        parent = cls
        while parent.parent:
            parent = parent.parent
            ancestors.append(parent)

        if not ascending:
            ancestors = ancestors[::-1]

        return ancestors

    @classmethod
    def family(cls):
        for ancestor in cls.ancestors():
            yield ancestor

        yield cls

        for descendant in cls.descendants():
            yield descendant


class FortnumDescriptor:
    def __init__(self, attr, fortnum, default=None, allow_none=False):
        self.values = WeakKeyDictionary()
        self.attr = attr
        self.fortnum = fortnum
        self.default = default
        self.allow_none = allow_none

    def __set__(self, instance, value):
        if value is None:
            if not self.allow_none and not self.default:
                raise ValueError("None not allowed.")

            if instance in self.values:
                del self.values[instance]

        else:
            if value not in self.fortnum:
                raise ValueError("'%s' is not a valid option for '%s'. Try %s" % (
                    value,
                    self.attr,
                    list(self.fortnum)
                ))
            self.values[instance] = value

    def __get__(self, instance, owner):
        if instance in self.values:
            return self.values[instance]
        return self.default
