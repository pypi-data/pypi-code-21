from decimal import Decimal

from shuup.core.models import ShopProduct


def get_product_price_min() -> Decimal:
    return _get_product_price_extreme(is_min=True)


def get_product_price_max() -> Decimal:
    return _get_product_price_extreme(is_max=True)


def _get_product_price_extreme(is_min = False, is_max = False) -> Decimal:
    if is_min:
        order_by_value = 'default_price_value'
    elif is_max:
        order_by_value = '-default_price_value'
    # noinspection PyUnboundLocalVariable
    product_with_min_price = ShopProduct.objects.order_by(order_by_value).first()
    if product_with_min_price:
        price = product_with_min_price.default_price.value
    else:
        price = 0
    return price
