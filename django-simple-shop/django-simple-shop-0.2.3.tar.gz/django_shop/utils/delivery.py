# coding=utf8
from __future__ import unicode_literals, absolute_import

from decimal import Decimal

from .hooks import HooksManager

_delivery_manager = None

METHOD_FREE = 'free'
METHOD_CONSTANT = 'constant'
METHOD_PERCENT = 'percent'
METHOD_API = 'api'
PRICING_METHODS = (
    (METHOD_FREE, 'Бесплатно'),
    (METHOD_CONSTANT, 'Заданная цена'),
    (METHOD_PERCENT, 'Процент от стоимости'),
    (METHOD_API, 'Получение по API'),
)


def compute_price_and_address(method, options, address, order_price, weight,
                              measures):
    """Получить цену доставки и ее реальный адрес.

    Дополнительные данные о параметрах заказа нужны для расчета реальной цены
    в службе доставки

    :type method: str
    :param method: Метод расчета цены доставки
    :type options: dict
    :param options: дополнительные параметры доставки
    :type address: dict[str, ANY]
    :param address: Данные об адресе доставки
    :type order_price: decimal.Decimal
    :param order_price: стоимость заказа
    :type weight: int
    :param weight: вес заказа в граммах
    :type measures: (int, int, int)
    :param measures: высота, ширина и глубина коробки, в которой поедет заказ

    :rtype: (decimal.Decimal, dict[str, ANY])
    :return: Цена доставки и ее реальный адрес
    """
    price = 0
    if method == METHOD_FREE:
        price = 0
    elif method == METHOD_CONSTANT:
        price = options['type_price']
    elif method == METHOD_PERCENT:
        price = round(options['type_price'] * Decimal(order_price) / Decimal(100)) + 1
    elif method == METHOD_API or options['hook']:
        delivery = create_delivery_obj(
            options['hook'],
            {
                'options': options,
                'weight': weight,
                'measures': measures,
                'order_price': order_price,
                'address': address,
            }
        )
        if method == METHOD_API:
            price = delivery.price
        address = delivery.address

    if not isinstance(price, Decimal):
        price = Decimal(price)

    return price, address


def get_widget_scripts(options):
    delivery = get_delivery_obj(options['hook'], {'options': options})
    return delivery.get_widget_scripts()


def create_delivery_obj(hook_name, order):
    if _delivery_manager is None:
        raise RuntimeError('Payment manager was not initiated')

    return _delivery_manager.create_object(hook_name, order)


def get_delivery_obj(hook_name, order):
    if _delivery_manager is None:
        raise RuntimeError('Payment manager was not initiated')

    return _delivery_manager.get_object(hook_name, order)


def get_model_choices():
    if _delivery_manager is None:
        raise RuntimeError('Payment manager was not initiated')

    return _delivery_manager.get_model_choices()


def get_description(hook_name):
    if _delivery_manager is None:
        raise RuntimeError('Payment manager was not initiated')

    return _delivery_manager.get_description(hook_name)


def initiate_delivery_manager(hooks):
    global _delivery_manager
    _delivery_manager = HooksManager(hooks, allow_empty=True)
