import ipaddress
import json
import string
import re

from hypothesis import strategies as st
from hypothesis.extra.fakefactory import fake_factory

from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework.utils.field_mapping import ClassLookupDict
from string import printable


__all__ = ('from_serializer', 'from_field')


def from_field(field, *, empty=empty):
    """
    Return strategy that creates valid data for field

    May provide `empty` if field is not required
    """
    # Make it easy to override
    if hasattr(field, 'hypothesis_strategy'):
        return field.hypothesis_strategy

    strategy = _strategies[field](field)

    if not field.required:
        strategy = st.one_of(st.just(empty), strategy)

    return strategy


def from_serializer(serializer, **extra):
    """
    Return strategy that creates valid data for serializer
    """
    if extra:
        raise NotImplementedError("TODO")

    if isinstance(serializer, serializers.BaseSerializer):
        instance = serializer
    else:
        instance = serializer()

    strategy = {
        name: from_field(field)
        for name, field in instance.fields.items()}

    return st.fixed_dictionaries(strategy).map(
        lambda result: {
            key: value
            for key, value in result.items()
            if value is not empty
        })


_url_strategy = fake_factory('uri')


def _slug_strategy(field):
    if field.allow_unicode:
        # TODO: Hyphens missing
        return st.from_regex(re.compile(r'^[^\W/]+\Z', re.UNICODE))
    else:
        return st.from_regex(re.compile(r'^[-a-zA-Z0-9_]+$'))


def _charfield_strategy(field):
    min_size = field.min_length
    if min_size is None and not field.allow_blank:
        min_size = 1

    max_size = field.max_length

    # TODO trim_whitespace is annoying, this excludes too much
    if field.trim_whitespace:
        blacklist_categories = ('Cc', 'Zs')
        characters = st.characters(blacklist_categories=blacklist_categories)
    else:
        characters = st.characters()

    return st.text(
        characters,
        min_size=min_size,
        max_size=max_size,
    )


def _multiplechoice_strategy(field):
    return st.lists(
        st.sampled_from(field.choices),
        max_size=len(field.choices),
        unique=True)


def _decimal_strategy(field):
    # Bound based on available number of digits
    d_max = max(0, 10**(field.max_digits - field.decimal_places) - 1)
    d_min = -1 * d_max

    # Explicit bound from field
    min_value = max(d_min, field.min_value) if field.min_value is not None else d_min
    max_value = min(d_max, field.max_value) if field.max_value is not None else d_max

    # TODO could have more places in between 0 and field.decimal_places
    return (
        st.integers(min_value=min_value, max_value=max_value) |
        st.decimals(min_value=min_value, max_value=max_value, places=field.decimal_places)
    )


def _list_strategy(field):
    min_size = field.min_length
    if min_size is None and not field.allow_empty:
        min_size = 1

    return st.lists(
        from_field(field.child),
        max_size=field.max_length,
        min_size=min_size,
    )


def _dict_strategy(field):
    values = from_field(field.child)
    return st.dictionaries(st.text(), values)


_json = st.recursive(
    st.none() | st.booleans() | st.floats(allow_infinity=False, allow_nan=False) | st.text(printable),
    lambda children: st.lists(children) | st.dictionaries(st.text(printable), children),
    max_leaves=5)


def _json_strategy(field):
    strategy = _json

    if field.allow_null is False:
        strategy = strategy.filter(lambda x: x is not None)

    if field.binary:
        strategy = st.builds(json.dumps, strategy)

    return strategy


_ipv4_strategy = st.builds(
        ipaddress.IPv4Address,
        st.integers(min_value=0, max_value=(2 ** 32 - 1))
    ).map(str)


_ipv6_strategy = st.builds(
        ipaddress.IPv6Address,
        st.integers(min_value=0, max_value=(2 ** 64 - 1))
    ).map(str)


def _ipaddress_strategy(field):
    if field.protocol == 'both':
        return st.one_of(_ipv4_strategy, _ipv6_strategy)
    elif field.protocol == 'ipv4':
        return _ipv4_strategy
    elif field.protocol == 'ipv6':
        return _ipv6_strategy

    raise ValueError("Unexpected protocol for: %s" % field)


def _related_strategy(field):
    def draw():
        # TODO do a random draw
        res = field.queryset.all().first()

        if res is None:
            return empty

        return field.to_representation(res)

    return st.builds(draw)


def _unsupported(field):
    raise ValueError("Unsupported field: %s" % field)


# Taken from hypothesis.provisional
@st.defines_strategy_with_reusable_values
def _domains():
    """A strategy for :rfc:`1035` fully qualified domain names."""
    atoms = st.text(string.ascii_letters + '0123456789-',
                    min_size=1, max_size=63
                    ).filter(lambda s: '-' not in s[0] + s[-1])
    return st.builds(
        lambda x, y: '.'.join(x + [y]),
        st.lists(atoms, min_size=1),
        # TODO: be more devious about top-level domains
        st.sampled_from(['com', 'net', 'org', 'biz', 'info'])
    ).filter(lambda url: len(url) <= 255)


@st.defines_strategy_with_reusable_values
def _emails():
    """A strategy for email addresses.
    See https://github.com/HypothesisWorks/hypothesis-python/issues/162
    for work on a permanent replacement.
    """
    local_chars = string.ascii_letters + string.digits + "!#$%&'*+-/=^_`{|}~"
    local_part = st.text(local_chars, min_size=1, max_size=64)
    # TODO: include dot-atoms, quoted strings, escaped chars, etc in local part
    return st.builds('{}@{}'.format, local_part, _domains()).filter(
        lambda addr: len(addr) <= 255)


_strategies = ClassLookupDict({
    serializers.BaseSerializer: from_serializer,
    serializers.ListSerializer: lambda f: st.lists(from_serializer(f.child), max_size=3),

    serializers.RelatedField: _related_strategy,
    serializers.StringRelatedField: lambda f: st.just(empty),
    serializers.HyperlinkedIdentityField: lambda f: st.just(empty),

    # Could do with some optimization, sample all values at once
    serializers.ManyRelatedField: lambda f: st.lists(_related_strategy(f.child_relation), max_size=3),

    serializers.CharField: _charfield_strategy,
    serializers.ListField: _list_strategy,
    serializers.DictField: _dict_strategy,
    serializers.JSONField: _json_strategy,
    serializers.IPAddressField: _ipaddress_strategy,
    serializers.DecimalField: _decimal_strategy,
    serializers.SlugField: _slug_strategy,
    serializers.URLField: lambda f: _url_strategy,
    serializers.EmailField: lambda f: _emails(),
    serializers.MultipleChoiceField: _multiplechoice_strategy,
    serializers.ChoiceField: lambda f: st.sampled_from(f.choices),
    serializers.IntegerField: lambda f: st.integers(min_value=f.min_value, max_value=f.max_value),
    serializers.FloatField: lambda f:  st.floats(min_value=f.min_value, max_value=f.max_value),
    serializers.BooleanField: lambda f: st.booleans(),
    serializers.NullBooleanField: lambda f: st.one_of(st.none(), st.booleans()),
    serializers.DateField: lambda f: st.dates(),
    serializers.DateTimeField: lambda f: st.datetimes(),
    serializers.TimeField: lambda f: st.times(),
    serializers.DurationField: lambda f: st.timedeltas(),
    serializers.UUIDField: lambda f: st.uuids(),
    serializers.RegexField: lambda f: st.from_regex(f.validators[0].regex),
    serializers.ReadOnlyField: lambda f: st.none(),
    serializers.HiddenField: lambda f: st.none(),
    serializers.SerializerMethodField: lambda f: st.none(),
    serializers.Field: _unsupported,
})
