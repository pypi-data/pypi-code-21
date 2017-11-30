from shuup.core.models import Product

from shuup_testutils.cases import SnakeTestCase
from shuup_testutils.generators import ShuupModelsGen


class ShuupModelsGenTest(SnakeTestCase):
    @classmethod
    def set_up_class(cls):
        cls.gen = ShuupModelsGen()
    
    def test_person_contact(self):
        self.gen.person_contact()

    def test_products_amount(self):
        products_count_expected = 20
        self.gen.products(amount=products_count_expected)
        products_count = Product.objects.all().count()
        self.assert_equal(products_count_expected, products_count)
