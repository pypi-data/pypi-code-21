
TEXT_LOOKUPS = [
    'exact',
    'iexact',
    'in',
    'contains',
    'icontains',
    'startswith',
    'istartswith',
    'endswith',
    'iendswith',
    'regex',
    'iregex'
]

CHOICES_LOOKUPS = [
    'exact',
    'in'
]

RANGE_LOOKUPS = [
    'exact',
    'isnull',
    'gt',
    'gte',
    'lt',
    'lte'
]

DATETIME_LOOKUPS = RANGE_LOOKUPS + [
    'date__exact',
    'date__gt',
    'date__gte',
    'date__lt',
    'date__lte'
]
