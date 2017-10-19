import textwrap
from operator import attrgetter
from warnings import warn

from fusion_util.errors import InvalidEnumItem



class Enum(object):
    """
    An enumeration.

    `Enum` objects implement the iterator protocol.

    :type _order: ``List[`EnumItem`]``
    :ivar _order: Enumeration items in the original order of the definition.

    :type _values: ``Mapping[object, `EnumItem`]``
    :ivar _values: A mapping of enumeration values to `EnumItem`s
    """
    def __init__(self, doc, values, value_key=attrgetter('value')):
        """
        :param str doc: Brief documentation of the enumeration.
        :type values: ``List[`EnumItem`]``
        :param values: List of enumeration items.
        :type value_key: ``Callable[[`EnumItem`], unicode]``
        :param value_key: Function to produce the key to use when constructing
        a mapping for each item in ``values``.
        """
        self.doc = doc
        _order = self._order = []
        _values = self._values = {}
        for value in values:
            key = value_key(value)
            if key in _values:
                raise ValueError(
                    '{!r} is already a value in the enumeration'.format(key))
            _order.append(value)
            _values[key] = value


    def __iter__(self):
        for item in self._order:
            if not item.hidden:
                yield item


    def __repr__(self):
        lines = textwrap.wrap(textwrap.dedent(self.doc.strip()))
        line = 'undocumented'
        if lines:
            line = lines[0]
            if len(lines) > 1:
                line += '...'
            line = '"""{}"""'.format(line)
        return '<{} {}>'.format(
            type(self).__name__,
            line)


    def __eq__(self, other):
        if isinstance(other, Enum):
            return (other.doc == self.doc and
                    self._order == other._order)
        return NotImplemented


    @classmethod
    def from_pairs(cls, doc, pairs):
        """
        Construct an enumeration from an iterable of pairs.

        :param doc: See `Enum.__init__`.
        :type pairs: ``Iterable[Tuple[unicode, unicode]]``
        :param pairs: Iterable to construct the enumeration from.
        :rtype: Enum
        """
        values = (EnumItem(value, desc) for value, desc in pairs)
        return cls(doc=doc, values=values)


    @classmethod
    def fromPairs(cls, doc, pairs):
        warn('Enum.fromPairs is deprecated, use Enum.from_pairs',
             DeprecationWarning, 2)
        return cls.from_pairs(doc, pairs)


    def get(self, value):
        """
        Get an enumeration item for an enumeration value.

        :param unicode value: Enumeration value.
        :raise InvalidEnumItem: If ``value`` does not match any known
        enumeration value.
        :rtype: EnumItem
        """
        _nothing = object()
        item = self._values.get(value, _nothing)
        if item is _nothing:
            raise InvalidEnumItem(value)
        return item


    def desc(self, value):
        """
        Get the enumeration item description for an enumeration value.

        :param unicode value: Enumeration value.
        """
        try:
            return self.get(value).desc
        except InvalidEnumItem:
            return u''


    def getDesc(self, value):
        warn('Enum.getDesc is deprecated, use Enum.desc',
             DeprecationWarning, 2)
        return self.desc(value)


    def extra(self, value, extra_name, default=None):
        """
        Get the additional enumeration value for ``extra_name``.

        :param unicode value: Enumeration value.
        :param str extra_name: Extra name.
        :param default: Default value in the case ``extra_name`` doesn't exist.
        """
        try:
            return self.get(value).get(extra_name, default)
        except InvalidEnumItem:
            return default


    def getExtra(self, value, extraName, default=None):
        warn('Enum.getExtra is deprecated, use Enum.extra',
             DeprecationWarning, 2)
        return self.extra(value, extraName, default)


    def find(self, **names):
        """
        Find the first item with matching extra values.

        :param \*\*names: Extra values to match.
        :rtype: `EnumItem`
        :return: First matching item or ``None``.
        """
        for res in self.find_all(**names):
            return res
        return None


    def find_all(self, **names):
        """
        Find all items with matching extra values.

        :param \*\*names: Extra values to match.
        :rtype: ``Iterable[`EnumItem`]``
        """
        values = names.items()
        if len(values) != 1:
            raise ValueError('Only one query is allowed at a time')
        name, value = values[0]
        for item in self:
            if item.get(name) == value:
                yield item


    def findAll(self, **names):
        warn('Enum.findAll is deprecated, use Enum.find_all',
             DeprecationWarning, 2)
        return self.find_all(**names)


    def as_pairs(self):
        """
        Transform the enumeration into a sequence of pairs.

        :rtype: ``List[Tuple[unicode, unicode]]``
        :return: List of enumeration value and description pairs.
        """
        return [(i.value, i.desc) for i in self]


    def asPairs(self):
        warn('Enum.asPairs is deprecated, use Enum.as_pairs',
             DeprecationWarning, 2)
        return self.as_pairs()



class ObjectEnum(Enum):
    """
    An enumeration for arbitrary Python objects.

    Pass the Python object as the `value` parameter to `EnumItem`, `ObjectEnum`
    will automatically create an ``id`` extra value for `EnumItem`\s that do
    not already have such a value.
    """
    def __init__(self, doc, values):
        def value_key(value):
            key = unicode(id(value.value))
            if value.get('id') is None:
                value._extra['id'] = key
            return key
        super(ObjectEnum, self).__init__(
            doc=doc, values=values, value_key=value_key)


    def get(self, value):
        value = unicode(id(value))
        return super(ObjectEnum, self).get(value)


    def as_pairs(self):
        return [(i.id, i.desc)
                for i in self]



class EnumItem(object):
    """
    An enumeration item contained by `Enum`.

    :ivar value: Enumeration value.
    :ivar unicode desc: Brief textual description of the enumeration item.
    :ivar bool hidden: Is this enumeration item hidden?
    :type _extra: ``Mapping[str, object]``
    :ivar _extra: Mapping of names to additional enumeration values.
    """
    def __init__(self, value, desc, hidden=False, **extra):
        """
        Initialise an enumeration item.

        :param value: See `EnumItem.value`.
        :param desc: See `EnumItem.desc`.
        :param hidden: See `EnumItem.hidden`.
        :param \*\*extra: Additional extra values, accessed via `EnumItem.get`.
        """
        self.value = value
        self.desc = desc
        self.hidden = hidden
        self._extra = extra


    def __repr__(self):
        return '<{} value={!r} desc={!r} hidden={}>'.format(
            type(self).__name__,
            self.value,
            self.desc,
            self.hidden)


    def __eq__(self, other):
        if isinstance(other, EnumItem):
            return (self.value == other.value and
                    self.desc == other.desc and
                    self.hidden == other.hidden and
                    self._extra == other._extra)
        return NotImplemented


    def __getattr__(self, name):
        """
        Get an extra value by name.
        """
        warn('Attribute access on EnumItem is deprecated, use EnumItem.get',
             DeprecationWarning, 2)
        if name in self._extra:
            return self.get(name)
        raise AttributeError(
            '{!r} object has no attribute {!r}'.format(
                type(self).__name__, name))


    def get(self, name, default=None):
        """
        Get the value of an extra parameter.

        :param str name: Extra parameter name.
        :param default: Default value in the case ``name`` doesn't exist.
        """
        return self._extra.get(name, default)


    def items(self):
        """
        Additional enumeration values.

        :rtype: ``Iterable[Tuple[str, object]]``
        """
        return self._extra.items()



def filter_enum(pred, enum):
    """
    Create a new enumeration containing only items filtered from another
    enumeration.

    Hidden enum items in the original enumeration are excluded.

    :type pred: ``Callable[[`EnumItem`], bool]``
    :param pred: Predicate that will keep items for which the result is true.
    :type enum: Enum
    :param enum: Enumeration to filter.
    :rtype: Enum
    :return: New filtered enumeration.
    """
    def _items():
        for item in enum:
            yield EnumItem(
                item.value,
                item.desc,
                not pred(item),
                **item._extra)
    return Enum('Filtered from {!r}'.format(enum), list(_items()))
