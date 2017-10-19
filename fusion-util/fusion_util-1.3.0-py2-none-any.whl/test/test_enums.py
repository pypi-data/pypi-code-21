from operator import methodcaller

from testtools import TestCase
from testtools.matchers import AfterPreprocessing as After
from testtools.matchers import (
    Contains, Equals, HasLength, Is, IsDeprecated, MatchesAll, MatchesListwise,
    MatchesStructure, Not, raises)

from fusion_util.enums import Enum, EnumItem, filter_enum, ObjectEnum
from fusion_util.errors import InvalidEnumItem



class EnumItemTests(TestCase):
    """
    Tests for `fusion_util.enums.EnumItem`.
    """
    def test_repr(self):
        """
        `EnumItem` has a useful representation that contains the value,
        description and hidden state.
        """
        self.assertThat(
            repr(EnumItem(u'foo', u'Foo')),
            Equals("<EnumItem value=u'foo' desc=u'Foo' hidden=False>"))

        self.assertThat(
            repr(EnumItem(u'foo', u'Foo', hidden=True)),
            Equals("<EnumItem value=u'foo' desc=u'Foo' hidden=True>"))


    def test_equal(self):
        """
        `EnumItem`\s can be compared for equality.
        """
        self.assertThat(
            EnumItem(u'1', u'One', hello=42),
            Equals(EnumItem(u'1', u'One', hello=42)))


    def test_not_equal(self):
        """
        `EnumItem`\s can be compared for inequality.
        """
        hello1 = object()
        hello2 = object()
        self.assertThat(
            EnumItem(u'1', u'One', hello=hello1),
            Not(Equals(EnumItem(u'1', u'One', hello=hello2))))


    def test_not_enum_equal(self):
        """
        `EnumItem`\s cannot be compared for equality against non-`EnumItem`\s.
        """
        self.assertThat(
            EnumItem(u'1', u'One'),
            Not(Equals(42)))


    def test_items(self):
        """
        `EnumItem.items` produces an iterable of key-value pairs for additional
        enumeration values.
        """
        item = EnumItem(u'foo', u'Foo', a=1, b=u'2')
        self.assertThat(
            list(item.items()),
            After(sorted,
                  Equals([('a', 1), ('b', u'2')])))


    def test_getattr(self):
        """
        Additional enum values can be accessed like attributes.
        """
        item = EnumItem(u'foo', u'Foo', a=1)
        self.assertThat(item.a, Equals(1))


    def test_getattr_error(self):
        """
        Trying to access nonexistent additional enum values by attribute
        results in `AttributeError`.
        """
        item = EnumItem(u'foo', u'Foo', a=1)
        self.assertThat(
            lambda: item.b,
            raises(AttributeError))


    def test_getattr_deprecated(self):
        """
        `EnumItem.__getattr__` is deprecated.
        """
        item = EnumItem(u'foo', u'Foo', a=1)
        self.assertThat(
            lambda: item.a,
            IsDeprecated(Contains('use EnumItem.get')))



class GenericEnumTestsMixin(TestCase):
    """
    Tests that are relevant to `Enum` and `ObjectEnum`.
    """
    def test_equal(self):
        """
        `Enum`\s can be compared for equality.
        """
        values = [EnumItem(u'1', u'One'),
                  EnumItem(u'2', u'Two', hello=42)]
        self.assertThat(
            Enum('doc', values),
            Equals(Enum('doc', values)))


    def test_not_equal(self):
        """
        `Enum`\s can be compared for inequality.
        """
        values = [EnumItem(u'1', u'One'),
                  EnumItem(u'2', u'Two', hello=42)]
        self.assertThat(
            Enum('doc', values),
            Equals(Enum('doc', values)))
        self.assertThat(
            Enum('doc', values),
            Not(Equals(Enum('doc2', values))))
        self.assertThat(
            Enum('doc', values),
            Not(Equals(Enum('doc', values[:1]))))


    def test_not_enum_equal(self):
        """
        `Enum`\s cannot be compared for equality against non-`Enum`\s.
        """
        self.assertThat(
            Enum('doc', []),
            Not(Equals(42)))


    def test_duplicate_values(self):
        """
        Constructing an enumeration with duplicate values results in
        `ValueError` being raised.
        """
        values = [
            EnumItem(u'foo', u'Foo'),
            EnumItem(u'bar', u'Bar'),
            EnumItem(u'foo', u'Not Foo', quux=u'frob')]
        self.assertThat(
            lambda: Enum('doc', values),
            raises(ValueError))
        pairs = [(e.value, e.desc) for e in values]
        self.assertThat(
            lambda: Enum.from_pairs('doc', pairs),
            raises(ValueError))


    def test_from_pairs(self):
        """
        Construct an enumeration from an iterable of pairs.
        """
        pairs = [
            (u'foo', u'Foo'),
            (u'bar', u'Bar')]
        enum = Enum.from_pairs('doc', pairs)
        self.assertThat(enum.doc, Equals('doc'))
        self.assertThat(enum.as_pairs(), Equals(pairs))


    def test_desc(self):
        """
        Getting an enumeration item's description by value returns the
        description or an empty `unicode` string if no item is represented
        by the given value.
        """
        values = [
            EnumItem(u'foo', u'Foo', hidden=True),
            EnumItem(u'bar', u'Bar')]
        enum = Enum('doc', values)
        self.assertThat(
            [e.desc for e in enum],
            Equals([enum.desc(e.value) for e in enum]))
        self.assertThat(enum.desc(u'DOES_NOT_EXIST'), Equals(u''))


    def test_hidden(self):
        """
        Enumeration items that have their ``hidden`` flag set are not listed in
        the result of `Enum.as_pairs`.
        """
        values = [
            EnumItem(u'foo', u'Foo', hidden=True),
            EnumItem(u'bar', u'Bar'),
            EnumItem(u'pop', u'Pop')]
        enum = Enum('doc', values)
        enum.get(u'pop').hidden = True
        pairs = enum.as_pairs()
        self.assertThat(pairs, Equals([(u'bar', u'Bar')]))


    def test_iterator(self):
        """
        `Enum` implements the iterator protocol and will iterate over
        `EnumItem`s in the order originally specified, omitting `EnumItem`s
        that are marked as hidden.
        """
        items = [EnumItem(u'foo', u'Foo'),
                 EnumItem(u'bar', u'Bar'),
                 EnumItem(u'baz', u'Baz', hidden=True)]
        enum = Enum('Doc', items)
        # The hidden Enum is omitted.
        self.assertThat(list(enum), HasLength(2))
        for expected, item in zip(items, enum):
            self.assertThat(expected, Is(item))


    def test_find_invalid_usage(self):
        """
        Passing fewer or more than one query raises `ValueError`.
        """
        enum = Enum('doc', [])
        self.assertThat(enum.find, raises(ValueError))
        self.assertThat(
            lambda: enum.find(foo=u'a', bar=u'b'),
            raises(ValueError))


    def test_find_all_invalid_usage(self):
        """
        Passing fewer or more than one query raises `ValueError`.
        """
        enum = Enum('doc', [])
        self.assertThat(
            lambda: list(enum.find_all()),
            raises(ValueError))
        self.assertThat(
            lambda: list(enum.find_all(foo=u'a', bar=u'b')),
            raises(ValueError))


    def test_findAll_deprecated(self):
        """
        `Enum.findAll` is deprecated.
        """
        enum = Enum('doc', [])
        self.assertThat(
            lambda: enum.findAll(foo=u'a'),
            IsDeprecated(Contains('use Enum.find_all')))


    def test_getDesc_deprecated(self):
        """
        `Enum.getDesc` is deprecated.
        """
        enum = Enum('doc', [])
        self.assertThat(
            lambda: enum.getDesc(u'a'),
            IsDeprecated(Contains('use Enum.desc')))


    def test_getExtra_deprecated(self):
        """
        `Enum.getExtra` is deprecated.
        """
        enum = Enum('doc', [])
        self.assertThat(
            lambda: enum.getExtra(u'a', u'extra'),
            IsDeprecated(Contains('use Enum.extra')))


    def test_asPairs_deprecated(self):
        """
        `Enum.asPairs` is deprecated.
        """
        enum = Enum('doc', [])
        self.assertThat(
            lambda: enum.asPairs(),
            IsDeprecated(Contains('use Enum.as_pairs')))


    def test_fromPairs_deprecated(self):
        """
        `Enum.fromPairs` is deprecated.
        """
        self.assertThat(
            lambda: Enum.fromPairs('doc', []),
            IsDeprecated(Contains('use Enum.from_pairs')))



def enum_values_fixture():
    """
    Fixture suitable for use with `Enum`.
    """
    return [
        EnumItem(u'foo', u'Foo', quux=u'hello', frob=u'world'),
        EnumItem(u'bar', u'Bar', quux=u'goodbye'),
        EnumItem(u'doh', u'Doh', frob=u'world')]



class EnumTests(TestCase):
    """
    Tests for `fusion_util.enums.Enum`.
    """
    def test_as_pairs(self):
        """
        Representing an enumeration as a list of pairs.
        """
        values = enum_values_fixture()
        enum = Enum('doc', values)
        pairs = [(e.get('id', e.value), e.desc) for e in values]
        self.assertThat(enum.as_pairs(), Equals(pairs))


    def test_get(self):
        """
        Getting an enumeration item by value returns the relevant `EnumItem`
        instance or raises `InvalidEnumItem` in the case where no item is
        represented by the given value.
        """
        values = enum_values_fixture()
        enum = Enum('doc', values)
        self.assertThat(
            values,
            Equals([enum.get(e.value) for e in values]))
        self.assertThat(
            lambda: enum.get(u'DOES_NOT_EXIST'),
            raises(InvalidEnumItem))


    def test_get_extra(self):
        """
        Getting an enumeration item extra value by enumeration value returns
        the extra's value or a default value, defaulting to ``None``.
        """
        enum = Enum('doc', enum_values_fixture())
        self.assertThat(
            enum.extra(u'foo', 'quux'),
            Equals(u'hello'))
        self.assertThat(
            enum.extra(u'foo', 'frob'),
            Equals(u'world'))
        self.assertThat(
            enum.extra(u'bar', 'quux'),
            Equals(u'goodbye'))
        self.assertThat(
            enum.extra(u'bar', 'nope'),
            Is(None))
        self.assertThat(
            enum.extra(u'bar', 'nope', u''),
            Equals(u''))


    def test_extra(self):
        """
        Extra parameters are retrieved by `EnumItem.get` if they exist
        otherwise a default value is returned instead.
        """
        enum = Enum('doc', enum_values_fixture())
        self.assertThat(
            enum.get(u'foo').get('quux'),
            Equals(u'hello'))
        self.assertThat(
            enum.get(u'foo').get('frob'),
            Equals(u'world'))
        self.assertThat(
            enum.get(u'bar').get('quux'),
            Equals(u'goodbye'))
        self.assertThat(
            enum.get(u'bar').get('boop'),
            Is(None))
        self.assertThat(
            enum.get(u'bar').get('beep', 42),
            Equals(42))


    def test_repr(self):
        """
        `Enum` has a useful representation that contains the type name and the
        enumeration description.
        """
        self.assertThat(
            repr(Enum('Foo bar', [])),
            Equals('<Enum """Foo bar""">'))

        lorem = """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. In vitae sem
        felis, sit amet tincidunt est. Cras convallis, odio nec accumsan
        vestibulum, lectus dolor feugiat magna, sit amet tempus lorem diam ac
        enim. Curabitur nisl nibh, bibendum ac tempus non, blandit ac turpis.
        """

        self.assertThat(
            repr(Enum(lorem, [])),
            Equals('<Enum """Lorem ipsum dolor sit amet, consectetur '
                   'adipiscing elit. In vitae sem...""">'))


    def test_repr_undocumented(self):
        """
        `Enum` has a useful representation even when the enumeration has no
        description.
        """
        self.assertThat(repr(Enum('', [])), Equals('<Enum undocumented>'))


    def test_find(self):
        """
        Finding an enumeration item by extra value gets the first matching item
        or ``None`` if there are no matches.
        """
        values = enum_values_fixture()
        enum = Enum('doc', values)
        self.assertThat(enum.find(quux=u'hello'), Is(values[0]))
        self.assertThat(enum.find(frob=u'world'), Is(values[0]))
        self.assertThat(enum.find(quux=u'goodbye'), Is(values[1]))
        self.assertThat(enum.find(haha=u'nothanks'), Is(None))


    def test_find_all(self):
        """
        Finding all enumeration items by extra value gets an iterable of all
        matching items. Passing fewer or more than one query raises
        `ValueError`.
        """
        values = enum_values_fixture()
        enum = Enum('doc', values)
        results = list(enum.find_all(frob=u'world'))
        self.assertThat(
            results,
            Equals([values[0], values[2]]))
        self.assertThat(
            enum.find_all(asdf=u'qwer'),
            After(list, Equals([])))



def object_enum_values_fixture(object1, object2, object3):
    """
    Fixture suitable for use with `ObjectEnum`.
    """
    return [
        EnumItem(object1, u'Foo', quux=u'hello', frob=u'world'),
        EnumItem(object2, u'Bar', quux=u'goodbye'),
        EnumItem(object3, u'Doh', frob=u'world', id=u'chuck')]



class ObjectEnumTests(TestCase):
    """
    Tests for `fusion_util.enums.ObjectEnum`.
    """
    def test_as_pairs(self):
        """
        Representing an enumeration as a list of pairs.
        """
        object1, object2, object3 = object(), object(), object()
        values = object_enum_values_fixture(object1, object2, object3)
        enum = ObjectEnum('doc', values)
        pairs = [(e.get('id', e.value), e.desc) for e in values]
        self.assertThat(enum.as_pairs(), Equals(pairs))


    def test_get(self):
        """
        Getting an enumeration item by value returns the relevant `EnumItem`
        instance or raises `InvalidEnumItem` in the case where no item is
        represented by the given value.
        """
        object1, object2, object3 = object(), object(), object()
        values = object_enum_values_fixture(object1, object2, object3)
        enum = ObjectEnum('doc', values)
        self.assertThat(
            values,
            Equals([enum.get(e.value) for e in values]))
        self.assertThat(
            lambda: enum.get(u'DOES_NOT_EXIST'),
            raises(InvalidEnumItem))


    def test_id_extra(self):
        """
        `ObjectEnum` automatically creates an ``id`` `EnumItem` extra value,
        based on the result of `id`, if one does not already exist.
        """
        object1, object2, object3 = object(), object(), object()
        values = object_enum_values_fixture(object1, object2, object3)
        enum = ObjectEnum('doc', values)
        self.assertThat(
            [e.get('id') for e in enum],
            MatchesListwise([
                Equals(unicode(id(object1))),
                Equals(unicode(id(object2))),
                Equals(u'chuck')]))


    def test_get_extra(self):
        """
        Getting an enumeration item extra value by enumeration value returns
        the extra's value or a default value, defaulting to ``None``.
        """
        object1, object2, object3 = object(), object(), object()
        values = object_enum_values_fixture(object1, object2, object3)
        enum = ObjectEnum('doc', values)
        self.assertThat(
            enum.extra(object1, 'quux'),
            Equals(u'hello'))
        self.assertThat(
            enum.extra(object1, 'frob'),
            Equals(u'world'))
        self.assertThat(
            enum.extra(object2, 'quux'),
            Equals(u'goodbye'))
        self.assertThat(
            enum.extra(u'bar', 'nope'),
            Is(None))
        self.assertThat(
            enum.extra(u'bar', 'nope', u''),
            Equals(u''))


    def test_extra(self):
        """
        Extra parameters are retrieved by `EnumItem.get` if they exist
        otherwise a default value is returned instead.
        """
        object1, object2, object3 = object(), object(), object()
        values = object_enum_values_fixture(object1, object2, object3)
        enum = ObjectEnum('doc', values)
        self.assertThat(
            enum.get(object1).get('quux'),
            Equals(u'hello'))
        self.assertThat(
            enum.get(object1).get('frob'),
            Equals(u'world'))
        self.assertThat(
            enum.get(object2).get('quux'),
            Equals(u'goodbye'))
        self.assertThat(
            enum.get(object2).get('boop'),
            Is(None))
        self.assertThat(
            enum.get(object2).get('beep', 42),
            Equals(42))


    def test_repr(self):
        """
        `ObjectEnum` has a useful representation that contains the type name
        and the enumeration description.
        """
        self.assertThat(
            repr(ObjectEnum('Foo bar', [])),
            Equals('<ObjectEnum """Foo bar""">'))

        lorem = """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. In vitae sem
        felis, sit amet tincidunt est. Cras convallis, odio nec accumsan
        vestibulum, lectus dolor feugiat magna, sit amet tempus lorem diam ac
        enim. Curabitur nisl nibh, bibendum ac tempus non, blandit ac turpis.
        """

        self.assertThat(
            repr(ObjectEnum(lorem, [])),
            Equals('<ObjectEnum """Lorem ipsum dolor sit amet, consectetur '
                   'adipiscing elit. In vitae sem...""">'))


    def test_find(self):
        """
        Finding an enumeration item by extra value gets the first matching item
        or ``None`` if there are no matches.
        """
        object1, object2, object3 = object(), object(), object()
        values = object_enum_values_fixture(object1, object2, object3)
        enum = ObjectEnum('doc', values)
        self.assertThat(enum.find(quux=u'hello'), Is(values[0]))
        self.assertThat(enum.find(frob=u'world'), Is(values[0]))
        self.assertThat(enum.find(quux=u'goodbye'), Is(values[1]))
        self.assertThat(enum.find(haha=u'nothanks'), Is(None))


    def test_find_all(self):
        """
        Finding all enumeration items by extra value gets an iterable of all
        matching items. Passing fewer or more than one query raises
        `ValueError`.
        """
        object1, object2, object3 = object(), object(), object()
        values = object_enum_values_fixture(object1, object2, object3)
        enum = ObjectEnum('doc', values)
        results = list(enum.find_all(frob=u'world'))
        self.assertThat(
            results,
            Equals([values[0], values[2]]))
        self.assertThat(
            enum.find_all(asdf=u'qwer'),
            After(list, Equals([])))



class FilterEnumTests(TestCase):
    """
    Tests for `fusion_util.enums.filter_enum`.
    """
    def test_stay_hidden(self):
        """
        Items that are hidden are not accidentally resurrected.
        """
        enum = Enum(
            'doc',
            [EnumItem(u'1', u'Option One'),
             EnumItem(u'2', u'Option Two', hidden=True)])
        self.assertThat(
            list(filter_enum(methodcaller('get', 'hidden'), enum)),
            Equals([]))


    def test_filter(self):
        """
        Filter items from an enumeration based on a predicate, ignoring hidden
        items.
        """
        enum = Enum(
            'doc',
            [EnumItem(u'1', u'Option One',
                      a=1),
             EnumItem(u'2', u'Option Two',
                      a=2, b=20, hidden=True),
             EnumItem(u'3', u'Option Three',
                      a=3, b=30),
             EnumItem(u'4', u'Option Four',
                      a=4),
             EnumItem(u'5', u'Option Five',
                      a=5)])
        self.assertThat(
            filter_enum(methodcaller('get', 'b'), enum),
            After(list,
                  MatchesListwise([
                      MatchesAll(
                          MatchesStructure(
                              value=Equals(u'3'),
                              desc=Equals(u'Option Three'),
                              hidden=Equals(False)),
                          After(lambda ei: sorted(ei.items()),
                                Equals([('a', 3), ('b', 30)])))])))
