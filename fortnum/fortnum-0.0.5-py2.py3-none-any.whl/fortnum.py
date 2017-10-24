from collections import OrderedDict, Sized
from weakref import WeakKeyDictionary

from fortnum.utils import OrderedSet


class FortnumException(Exception):
    pass


class DuplicatedFortnum(FortnumException):
    pass


class FortnumDoesNotExist(FortnumException):
    pass


class MultipleParents(FortnumException):
    pass


class class_property(classmethod):
    def __get__(self, instance, owner):
        return super().__get__(instance, owner)()


class FortnumRelation:
    def __init__(self, related_name, many=False):
        self.related_name = related_name
        self.many = many


class FortnumMeta(type):
    _registry = {}

    @classmethod
    def __prepare__(mcs, name, bases):
        return OrderedDict()

    def __new__(mcs, name, bases, classdict):
        # Allow name override when using class declaration by explicitly providing a "__name__"
        # if "asdf" in classdict:
        #     print(classdict["asdf"])
        #     name = classdict["asdf"]

        if name in mcs._registry:
            raise DuplicatedFortnum()

        # Create Fortnum class and add to registry
        fortnum = type.__new__(mcs, name, bases, dict(classdict))
        mcs._registry[name] = fortnum

        # Initialize fortnum attributes
        fortnum.parent = None
        fortnum.parents = OrderedSet()
        fortnum.parent_index = {}

        # Identify children and register parent connections
        if fortnum.item_class:
            fortnum.children = OrderedDict((
                (key, value)
                for key, value in classdict.items()
                if issubclass(type(value), fortnum.item_class))
            )

            for index, child in enumerate(fortnum.children.values()):
                if child.parent is None:
                    child.parent = fortnum
                child.parents.add(fortnum)
                child.parent_index[fortnum] = index

        else:
            fortnum.children = OrderedDict()

        for base in bases:
            # Find relations defined on base classes and add them to the objects.
            for key, relation in (
                    (key, relation)
                    for key, relation
                    in base.__dict__.items()
                    if issubclass(relation.__class__, FortnumRelation)
            ):
                related_fortnums = classdict[key] if relation.many else [classdict[key]]

                for related_fortnum in related_fortnums:
                    if related_fortnum:
                        if not hasattr(related_fortnum, relation.related_name):
                            setattr(related_fortnum, relation.related_name, set())
                        getattr(related_fortnum, relation.related_name).add(fortnum)

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
    item_class = FortnumMeta

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
