from decimal import Decimal
from parameterized import parameterized, param
from shuup_testutils.cases import ApiAuthAdminTestCase
from shuup_testutils.generators import ShuupModelsGen

from scatl.services.product.price import get_product_price_min, \
    get_product_price_max


class ProductUtilsTest(ApiAuthAdminTestCase):
    # noinspection PyArgumentList
    @parameterized.expand([
        param(price_min=Decimal('10'),   price_max=Decimal('500.1')),
        param(price_min=Decimal('11.5'), price_max=Decimal('600.8')),
        param(price_min=Decimal('500'),  price_max=Decimal('1000.1')),
    ])
    def test_price_min_and_max_getters(self, price_min: Decimal, price_max: Decimal):
        gen = ShuupModelsGen()
        gen.product(price=price_min)
        gen.product(price=price_max)
        
        self.assert_equal(price_min, get_product_price_min())
        self.assert_equal(price_max, get_product_price_max())
