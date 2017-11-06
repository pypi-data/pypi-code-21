import datetime
import ioex
import ioex.calcex
import ioex.reex
import locale
import pytz
import re
import yaml


class _Object(object):

    def __eq__(self, other):
        return type(self) == type(other) and vars(self) == vars(other)

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        return self.__class__.__name__ + '(%s)' % ', '.join([
            '%s=%r' % (k, v) for k, v in vars(self).items()
        ])


class _YamlInitConstructor(yaml.YAMLObject):

    @classmethod
    def from_yaml(cls, loader, node):
        return cls(**loader.construct_mapping(node, deep=True))
        # return cls(**{
        #     k: unicode(v) if isinstance(v, str) else v
        #         for (k, v) in loader.construct_mapping(node, deep = True).items()
        #     })

    @classmethod
    def register_yaml_constructor(cls, loader, tag=None):
        loader.add_constructor(
            cls.yaml_tag if tag is None else tag,
            cls.from_yaml,
        )


class _YamlVarsRepresenter(yaml.YAMLObject):

    @classmethod
    def to_yaml(cls, dumper, obj):
        return dumper.represent_mapping(
            cls.yaml_tag,
            {k: v for k, v in vars(obj).items()
                if v and (not isinstance(v, list) or len(v) > 0)},
        )


class Sum(ioex.calcex.Figure):

    currency_symbol_map = {
        '€': 'EUR',
        'US$': 'USD',
        '￥': 'CNY',
    }

    yaml_tag = u'!sum'

    def __init__(self, value=None, currency=None, unit=None):
        if not currency is None and not unit is None:
            raise ValueError('missing currency')
        else:
            unit = currency if currency else unit
            super(Sum, self).__init__(
                value=value,
                unit=currency if currency else unit,
            )

    def get_value(self):
        return super(Sum, self).get_value()

    def set_value(self, value):
        assert type(value) is float
        super(Sum, self).set_value(value)

    """ use property() instead of decorator to enable overriding """
    value = property(get_value, set_value)

    def get_unit(self):
        return super(Sum, self).get_unit()

    def set_unit(self, currency):
        currency = Sum.currency_symbol_map.get(currency, currency)
        assert type(currency) is str
        super(Sum, self).set_unit(currency)

    """ use property() instead of decorator to enable overriding """
    unit = property(get_unit, set_unit)
    currency = property(get_unit, set_unit)

    space_regex = '[\xa0 ]'
    value_regex = r"-?\d+([\.,]\d+)?"
    currency_regex = r"[^\d,\.\s-]+"
    sum_regex_value_first = r'\$?(?P<value>{}){}?(?P<currency>{})'.format(
        value_regex, space_regex, currency_regex,
    )
    sum_regex_currency_first = r'(?P<currency>{}){}?(?P<value>{})'.format(
        currency_regex, space_regex, value_regex,
    )
    sum_regex = r'({})'.format('|'.join([
        ioex.reex.rename_groups(
            sum_regex_value_first,
            lambda n: {'value': 'pre_value', 'currency': 'post_currency'}[n]
        ),
        ioex.reex.rename_groups(
            sum_regex_currency_first,
            lambda n: {'currency': 'pre_currency', 'value': 'post_value'}[n]
        ),
    ]))

    @staticmethod
    def parse_text(text):
        match = re.search('^{}$'.format(Sum.sum_regex), text, re.UNICODE)
        assert not match is None, '\n' + '\n'.join([
            'regex: {}'.format(Sum.sum_regex),
            'text: {}'.format(text),
            'text repr: {!r}'.format(text),
        ])
        attr = ioex.dict_collapse(
            match.groupdict(),
            lambda k: k.split('_')[-1],
        )
        return Sum(
            value=locale.atof(attr['value']),
            currency=attr['currency'],
        )


class _ItemCollection():

    def __init__(
            self,
            debitor_address=None,
            debitor_comment=None,
            items=None
            ):
        if debitor_address is not None:
            assert isinstance(debitor_address, str)
            self.debitor_address = debitor_address
        if debitor_comment is not None:
            assert isinstance(debitor_comment, str)
            self.debitor_comment = debitor_comment
        if items is not None:
            assert isinstance(items, list)
            assert all([isinstance(i, Item) for i in items])
            self.items = items
        else:
            self.items = []

    @property
    def items_total_price_brutto(self):
        return sum([i.total_price_brutto for i in self.items])


class Invoice(_Object, _ItemCollection, _YamlInitConstructor, _YamlVarsRepresenter):

    yaml_tag = u'!invoice'

    def __init__(self,
                 creditor,
                 debitor_id,
                 invoice_date,
                 invoice_id,
                 discounts=None,
                 invoice_url=None,
                 **kwargs
                 ):
        assert isinstance(creditor, str)
        self.creditor = creditor
        assert isinstance(invoice_id, str)
        self.invoice_id = invoice_id
        assert (isinstance(invoice_date, datetime.date)
                or isinstance(invoice_date, datetime.datetime))
        self.invoice_date = invoice_date
        assert isinstance(debitor_id, str)
        self.debitor_id = debitor_id
        if discounts:
            assert isinstance(discounts, list)
            assert all([isinstance(d, Discount) for d in discounts])
            self.discounts = discounts
        else:
            self.discounts = []
        if invoice_url:
            assert isinstance(invoice_url, str)
            self.invoice_url = invoice_url
        _ItemCollection.__init__(self, **kwargs)


class Order(_Object, _ItemCollection, _YamlInitConstructor, _YamlVarsRepresenter):

    yaml_tag = u'!order'

    def __init__(self, platform, order_id, order_date,
                 customer_id=None,
                 discounts=None,
                 platform_view_url=None,
                 **kwargs
                 ):
        assert type(platform) is str
        self.platform = platform
        if type(order_id) in [int]:
            order_id = str(order_id)
        assert type(order_id) is str
        self.order_id = order_id
        assert type(order_date) in [datetime.date, datetime.datetime]
        if type(order_date) is datetime.datetime and order_date.tzinfo:
            order_date = order_date.astimezone(pytz.utc)
        self.order_date = order_date
        if customer_id is not None:
            assert type(customer_id) is str
            self.customer_id = customer_id
        if discounts is None:
            self.discounts = []
        else:
            assert type(discounts) is list
            assert all([isinstance(d, Discount) for d in discounts])
            self.discounts = discounts
        if platform_view_url:
            assert isinstance(platform_view_url, str)
            self.platform_view_url = platform_view_url
        _ItemCollection.__init__(self, **kwargs)


class Distance(ioex.calcex.Figure):

    yaml_tag = u'!distance'

    def get_value(self):
        return super(Distance, self).get_value()

    def set_value(self, value):
        assert type(value) is float
        super(Distance, self).set_value(value)

    """ use property() instead of decorator to enable overriding """
    value = property(get_value, set_value)

    @property
    def metres(self):
        if self.unit == 'm':
            return Distance(self.value, 'm')
        elif self.unit == 'km':
            return Distance(self.value * 1000, 'm')
        else:
            raise Exception()


class Discount(_Object, _YamlInitConstructor):

    yaml_tag = u'!discount'

    def __init__(self, name=None, amount=None, code=None):
        assert type(name) is str
        self.name = name
        assert type(amount) is Sum
        assert amount.value >= 0
        self.amount = amount
        if code:
            assert isinstance(code, str)
            self.code = code


class Item(_Object, _YamlInitConstructor, _YamlVarsRepresenter):

    yaml_tag = u'!item'

    def __init__(self,
                 name=None,
                 price_brutto=None,
                 sub_items=None,
                 url=None,
                 ):
        if not name is None:
            assert type(name) is str
            self.name = name
        assert type(price_brutto) is Sum
        if sub_items is None:
            self.sub_items = []
        else:
            assert isinstance(sub_items, list)
            assert all([isinstance(i, Item) for i in sub_items])
            self.sub_items = sub_items
        self.price_brutto = price_brutto
        if url is not None:
            assert type(url) is str
            self.url = url

    @property
    def total_price_brutto(self):
        return self.price_brutto \
            + sum([s.price_brutto for s in self.sub_items])


class Campaign(_Object, _YamlInitConstructor):

    yaml_tag = u'!campaign'

    def __init__(self,
                 end=None,
                 founder=None,
                 name=None,
                 website_url=None,
                 ):
        assert type(name) is str
        self.name = name
        assert type(founder) is str
        self.founder = founder
        if not end is None:
            assert type(end) is datetime.datetime
            self.end = end
        if not website_url is None:
            assert type(website_url) is str
            self.website_url = website_url


class Pledge(Item):

    yaml_tag = u'!pledge'

    def __init__(self,
                 campaign=None,
                 reward=None,
                 **kwargs
                 ):
        super(Pledge, self).__init__(**kwargs)
        assert type(campaign) is Campaign
        self.campaign = campaign
        if not reward is None:
            assert type(reward) is str
            self.reward = reward


class Contribution(Item):

    yaml_tag = u'!contribution'

    def __init__(self,
                 campaign=None,
                 reward=None,
                 **kwargs
                 ):
        super(Contribution, self).__init__(**kwargs)
        assert type(campaign) is Campaign
        self.campaign = campaign
        if not reward is None:
            assert type(reward) is str
            self.reward = reward


class Article(Item):

    yaml_tag = u'!article'

    def __init__(self,
                 access_option=None,
                 authors=None,
                 color=None,
                 delivery_date=None,
                 depth=None,
                 features=None,
                 height=None,
                 maximum_load=None,
                 option=None,
                 product_id=None,
                 quantity=None,
                 release_date=None,
                 reseller=None,
                 shipper=None,
                 size=None,
                 state=None,
                 width=None,
                 **kwargs
                 ):
        super(Article, self).__init__(**kwargs)
        assert not self.name is None
        if quantity is not None:
            assert type(quantity) is int
            self.quantity = quantity
        if access_option is not None:
            assert type(access_option) is str
            self.access_option = access_option
        if authors is not None:
            assert type(authors) is list
            self.authors = authors
        if state is not None:
            assert type(state) is str
            self.state = state
        if release_date is not None:
            assert type(release_date) in [datetime.datetime, datetime.date]
            self.release_date = release_date
        if reseller is not None:
            assert type(reseller) is str
            self.reseller = reseller
        if shipper is not None:
            assert type(shipper) is str
            self.shipper = shipper
        if product_id is not None:
            if type(product_id) in [int]:
                product_id = str(product_id)
            assert type(product_id) is str
            self.product_id = product_id
        if option is not None:
            assert type(option) is str
            self.option = option
        if color is not None:
            assert type(color) is str
            self.color = color
        if size is not None:
            assert type(size) is str
            self.size = size
        if width is not None:
            assert type(width) is Distance
            self.width = width
        if depth is not None:
            assert type(depth) is Distance
            self.depth = depth
        if height is not None:
            assert type(height) is Distance
            self.height = height
        if maximum_load is not None:
            assert type(maximum_load) is ioex.calcex.Figure, type(maximum_load)
            self.maximum_load = maximum_load
        if features is not None:
            assert type(features) is str
            self.features = features
        if delivery_date is not None:
            assert type(delivery_date) is datetime.date
            self.delivery_date = delivery_date


class Service(Item):

    yaml_tag = u'!service'

    def __init__(self,
                 duration=None,
                 ip_addresses=None,
                 location=None,
                 period=None,
                 state=None,
                 **kwargs
                 ):
        super(Service, self).__init__(**kwargs)
        assert not (duration and period)
        if duration:
            assert isinstance(duration, ioex.datetimeex.Duration)
            self.duration = duration
        if ip_addresses:
            assert isinstance(ip_addresses, list)
            assert all([isinstance(a, str) for a in ip_addresses])
            self.ip_addresses = ip_addresses
        if location:
            assert isinstance(location, str)
            self.location = location
        if period:
            assert isinstance(period, ioex.datetimeex.Period)
            self.period = period
        if state:
            assert isinstance(state, str)
            self.state = state


class HostingService(Service):

    yaml_tag = u'!hosting-service'

    def __init__(self,
                 operating_system=None,
                 **kwargs
                 ):
        super(HostingService, self).__init__(**kwargs)
        if operating_system:
            assert isinstance(operating_system, str)
            self.operating_system = operating_system


class CloudMining(Service):

    yaml_tag = u'!cloud-mining'

    def __init__(self,
                 hashrate=None,
                 **kwargs
                 ):
        super(CloudMining, self).__init__(**kwargs)
        if hashrate:
            assert isinstance(hashrate, ioex.calcex.Figure)
            self.hashrate = hashrate


class Transportation(Item):

    yaml_tag = u'!transportation'

    def __init__(self,
                 arrival_time=None,
                 departure_point=None,
                 destination_point=None,
                 distance=None,
                 estimated_arrival_time=None,
                 passenger=None,
                 route_map=None,
                 ticket_url=None,
                 valid_from=None,
                 valid_until=None,
                 **kwargs
                 ):
        super(Transportation, self).__init__(**kwargs)
        if arrival_time is not None:
            assert isinstance(arrival_time, datetime.datetime) \
                or isinstance(arrival_time, ioex.datetimeex.Period)
            self.arrival_time = arrival_time
        if departure_point is not None:
            assert type(departure_point) is str
            self.departure_point = departure_point
        if destination_point is not None:
            assert type(destination_point) is str
            self.destination_point = destination_point
        if distance is not None:
            assert type(distance) is Distance
            self.distance = distance
        if route_map is not None:
            assert type(route_map) is bytes
            self.route_map = route_map
        if passenger is not None:
            assert type(passenger) is Person
            self.passenger = passenger
        if valid_from is not None:
            assert type(valid_from) is datetime.datetime
            assert not valid_from.tzinfo is None
            self.valid_from = valid_from
        if valid_until is not None:
            assert type(valid_until) is datetime.datetime
            assert not valid_until.tzinfo is None
            self.valid_until = valid_until
        if ticket_url is not None:
            assert type(ticket_url) is str
            self.ticket_url = ticket_url
        if estimated_arrival_time is not None:
            assert type(estimated_arrival_time) is ioex.datetimeex.Period
            assert not estimated_arrival_time.start.tzinfo is None
            assert not estimated_arrival_time.end.tzinfo is None
            self.estimated_arrival_time = estimated_arrival_time


class Shipping(Transportation):

    yaml_tag = u'!shipping'

    def __init__(self,
                 tracking_number=None,
                 **kwargs
                 ):
        super(Shipping, self).__init__(**kwargs)
        if tracking_number:
            assert isinstance(tracking_number, str)
            self.tracking_number = tracking_number


class TaxiRide(Transportation):

    yaml_tag = u'!taxi-ride'

    def __init__(self,
                 departure_time=None,
                 driver=None,
                 name=None,
                 **kwargs
                 ):
        if name is None:
            name = u'Taxi Ride'
        super(TaxiRide, self).__init__(name=name, **kwargs)
        assert type(driver) is str
        self.driver = driver
        assert departure_time is None or type(
            departure_time) is datetime.datetime
        self.departure_time = departure_time


class Person(_Object, _YamlInitConstructor):

    yaml_tag = u'!person'

    def __init__(self, first_name=None, last_name=None):
        self.first_name = first_name
        self.last_name = last_name

    @property
    def first_name(self):
        return self._first_name

    @first_name.setter
    def first_name(self, first_name):
        assert first_name is None or type(first_name) is str
        self._first_name = first_name

    @property
    def last_name(self):
        return self._last_name

    @last_name.setter
    def last_name(self, last_name):
        assert last_name is None or type(last_name) is str
        self._last_name = last_name

    @classmethod
    def to_yaml(cls, dumper, person):
        return dumper.represent_mapping(cls.yaml_tag, {
            'first_name': person.first_name,
            'last_name': person.last_name,
        })

    def __repr__(self):
        return self.__class__.__name__ + '(%s)' % ', '.join([
            '%s=%r' % (k, v) for k, v in vars(self).items()
        ])
