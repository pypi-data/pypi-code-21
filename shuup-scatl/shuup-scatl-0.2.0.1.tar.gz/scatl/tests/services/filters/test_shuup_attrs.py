from shuup.core.models import Attribute, AttributeType, Product

from scatl.tests.testutils.filters_test_case import FiltersTestCase


class ShuupAttrsFiltersTest(FiltersTestCase):
    def test_bool(self):
        product = self.gen.product()
        attr = Attribute.objects.create(
            identifier='ident',
            type=AttributeType.BOOLEAN,
            name='test name',
        )
        product.attributes.create(
            attribute=attr,
            numeric_value=1,
        )
        Product.objects.get(
            attributes__attribute__identifier=attr.identifier,
            attributes__numeric_value=1,
        )
