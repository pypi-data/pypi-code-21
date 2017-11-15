
def split_collection_slug(slug):
    slug_chunks = slug.split('/')
    collection_slug = slug_chunks[0]
    if len(slug_chunks) > 1:
        filter_chunks = slug_chunks[1:]
    else:
        filter_chunks = []
    return collection_slug, filter_chunks


def split_choices(line):
    pairs = line.split('|')
    result = {}
    for p in pairs:
        k, v = p.split('=', 1)
        if v:
            result.update({k: v})
    return result


def reverse_choices(line, prefix):
    choices = split_choices(line)
    result = dict([('%s:%s' % (prefix, a), b) for b, a in choices.items()])
    return result


def get_property_values_for_slugs():
    from .models import PropertyValueSlug
    return dict(PropertyValueSlug.objects.values_list('slug', 'value'))


def get_property_slugs():
    from .models import PropertyValueSlug
    return PropertyValueSlug.objects.values_list('value', 'slug')


def filter_slug_to_tags(collection, filter_chunks, trigger=None):
    from .models import Vendor
    import itertools
    _orig_filter_chunks = filter_chunks
    filter_tags = set()
    prices = (None, None)
    rules = collection.get_url_filter_rules()
    rules_table = [
        line.strip().split('/') for line in rules.splitlines() if not (line.startswith('#') or line.strip() == '')]

    excludes = []
    for rule in rules_table:
        if rule[0] == 'TAG' and rule[2] == 'CHOICE':
            choices = split_choices(rule[3])
            excludes += choices.keys()

    vendor_slugs = []
    filter_chunks = list(itertools.chain(*[c.split(';') for c in filter_chunks]))

    _allowed_vendor_slugs = {a: b for a, b in Vendor.objects.values_list('slug', 'id')}
    _check_price = False

    value_slugs = get_property_values_for_slugs()

    def get_value_for_slug(slug):
        return value_slugs.get(slug, slug)

    for chunk in filter_chunks:
        # Check by rule
        for rule in rules_table:
            if rule[0] == 'VENDOR' and chunk not in vendor_slugs and chunk in _allowed_vendor_slugs.keys():
                vendor_slugs.append(chunk)
            elif rule[0] == 'PRICE' and _check_price is False and chunk.startswith('price-'):
                _check_price = True
                _t = chunk.split('-')
                if len(_t) == 3:
                    try:
                        _from = float(_t[1])
                    except ValueError:
                        _from = None
                    try:
                        _to = float(_t[2])
                    except ValueError:
                        _to = None
                    prices = (_from, _to)
            elif rule[0] == 'TAG':
                cmd, prefix = rule[1][0], rule[1][1:]
                _tag = ''
                if cmd == '+' and chunk not in excludes and chunk.startswith(prefix):
                    if rule[2] == 'WITH PREFIX':
                        _tag = '%s:%s' % (prefix, get_value_for_slug(chunk))
                    elif rule[2] == 'VALUE ONLY':
                        _tag = '%s:%s' % (prefix, get_value_for_slug(chunk[len(prefix):]))
                    elif rule[2] == 'VALUE ONLY IGNORE DASH':
                        _tag = '%s:%s' % (prefix, get_value_for_slug(chunk[len(prefix)+1:]))
                    elif rule[2] == 'CHOICE':
                        choices = split_choices(rule[3])
                        if chunk in choices:
                            _tag = '%s:%s' % (prefix, get_value_for_slug(choices[chunk]))
                elif cmd == '-':
                    if rule[2] == 'CHOICE':
                        choices = split_choices(rule[3])
                        if chunk in choices:
                            _tag = '%s:%s' % (prefix, get_value_for_slug(choices[chunk]))
                if _tag:
                    filter_tags.add(_tag)
            elif rule[0] == 'NOT ALLOWED':
                choices = rule[1].split('|')
                if choices and set(choices).issubset(filter_tags):
                    if rule[2] == 'REMOVE':
                        filter_tags.remove(choices[int(rule[3])])

    vendors = Vendor.objects.filter(pk__in=[_allowed_vendor_slugs[i] for i in vendor_slugs]) if vendor_slugs else []

    filter_tags = list(filter_tags)
    normalized_f_tags = normalize_filter_tags(
        collection, vendors, prices,
        filter_tags, get_property_slugs(),
        rules,
        trigger=trigger,
    )
    if trigger is None:
        _redirect = _orig_filter_chunks != normalized_f_tags
    else:
        _redirect = ([trigger] + _orig_filter_chunks) != normalized_f_tags
    return filter_tags, vendors, prices, normalized_f_tags, _redirect


def group_tags_for_prefixes(tags):
    prefixes_and_tags = [t.split(':') for t in tags]
    prefixes = list(set([t[0] for t in prefixes_and_tags]))
    regrouped_tags = [
        [':'.join(t) for t in prefixes_and_tags if t[0] == x] for x in prefixes]
    return regrouped_tags


def regroup_tags_for_filter_sets(tags):
    import itertools
    regrouped_tags = group_tags_for_prefixes(tags)
    result = list(itertools.product(*regrouped_tags))
    return result


def get_tags_array_query_expression(tag_groups, fieldname):
    from django.db.models import Q
    expr = None
    for g in tag_groups:
        kwargs = {'%s__contains' % fieldname: list(g)}
        if expr is None:
            expr = Q(**kwargs)
        else:
            expr |= Q(**kwargs)
    return expr


def generate_tags_for_product(product):
    properties = product.product_type.properties.filter(use_in_filters=True)
    tags = []
    for p in properties:
        property_value = product.properties.get(p.title)
        if property_value is not None:
            tags.append(p.tag_prefix + property_value)
    return tags


def normalize_filter_tags(
        collection, vendors=[], prices=(None, None), tags=None, cached_value_slugs=None,
        cached_url_filter_rules=None, trigger=None):
    if tags is None:
        tags = []
    if cached_value_slugs is None:
        cached_value_slugs = []

    result = []
    if trigger is not None:
        result.append(trigger)

    rules = cached_url_filter_rules or collection.get_url_filter_rules()
    rules_table = [
        line.strip().split('/') for line in rules.splitlines() if not (line.startswith('#') or line.strip() == '')]

    value_slugs = dict(cached_value_slugs)

    def get_slug_for_value(value):
        return value_slugs.get(value, value)

    for rule in rules_table:
        if rule[0] == 'VENDOR' and vendors:
            _vendor_slugs = []
            for v in vendors:
                if type(v) is str:
                    _vendor_slugs.append(v)
                else:
                    _vendor_slugs.append(v.slug)
            result.append(';'.join(_vendor_slugs))
        elif rule[0] == 'PRICE' and (bool(prices[0]) or bool(prices[1])):
            result.append('price-%s-%s' % (prices[0] or 'none', prices[1] or 'none'))
        elif rule[0] == 'TAG':
            cmd, prefix = rule[1][0], rule[1][1:]
            _tags = sorted([t for t in tags if t.split(':')[0] == prefix])
            _chunk = ''

            if cmd == '+':
                if rule[2] == 'WITH PREFIX':
                    _chunk = ';'.join(['%s%s' % (prefix, get_slug_for_value(t.replace(':', ''))) for t in _tags])
                elif rule[2] == 'VALUE ONLY':
                    _chunk = ';'.join(['%s%s' % (prefix, get_slug_for_value(t[len(prefix)+1:])) for t in _tags])
                elif rule[2] == 'VALUE ONLY IGNORE DASH':
                    _chunk = ';'.join(['%s-%s' % (prefix, get_slug_for_value(t[len(prefix)+1:])) for t in _tags])
                elif rule[2] == 'CHOICE':
                    choices = reverse_choices(rule[3])
                    for c in choices:
                        if c in _tags:
                            _chunk = '%s%s' % (prefix, get_slug_for_value(choices[c]))
            elif cmd == '-':
                if rule[2] == 'CHOICE':
                    choices = reverse_choices(rule[3], prefix)
                    for c in choices:
                        if c in _tags:
                            _chunk = get_slug_for_value(choices[c])
            if _chunk:
                result.append(_chunk)

    # print('normalize_filter_tags', collection, vendors, prices, tags, '->', result)

    return result


def get_unique_tagset(products=None):
    """
    Returns the set of tags for the specified products or for all products.

    :param products: A Product queryset. If None function is working with
       all product base.
    :return: A set of tags.
    """
    import itertools
    if products is None:
        from .models import Product
        products = Product.objects.all()

    tagset = products.values_list('tags', flat=True)
    tagset = list(set(itertools.chain(*tagset)))
    return tagset


def filter_non_numeric_tags(tagset):
    """
    Returns a list of non numeric tags without prefixes for specified tagset.

    :param tagset: A set of tags.
    :return: A filtered list of tags without prefixes.
    """
    values = list(
        filter(
            lambda x: not x.isnumeric(),
            map(
                lambda x: x.split(':', 1)[-1],
                tagset,
            ),
        ))
    return values
