import factory
import factory.fuzzy

from django.contrib.contenttypes.models import ContentType

from . import models


class AbstractItemFactory(factory.django.DjangoModelFactory):
    price = factory.fuzzy.FuzzyFloat(1, 100)
    tax_rate = factory.fuzzy.FuzzyFloat(100)

    class Meta:
        abstract = True


class ItemFactory(AbstractItemFactory):
    name = factory.fuzzy.FuzzyText(length=255)
    image = factory.django.ImageField()

    class Meta:
        model = 'orders.Item'


class ItemInOrderFactory(AbstractItemFactory):
    item = factory.SubFactory('orders.factories.ItemFactory')
    order = factory.SubFactory('orders.factories.OrderFactory')
    quantity = factory.fuzzy.FuzzyInteger(1, 10)

    class Meta:
        model = 'orders.ItemInOrder'


class PayPalIPN(factory.django.DjangoModelFactory):

    class Meta:
        model = 'ipn.PayPalIPN'


class OrderFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory('core_flavor.factories.UserFactory')
    currency = factory.SubFactory('countries.factories.CurrencyFactory')

    content_type = factory.LazyAttribute(
        lambda obj: ContentType.objects.get_for_model(obj.payment_method)
    )

    object_id = factory.SelfAttribute('payment_method.id')
    payment_method = factory.SubFactory(PayPalIPN)

    status = factory.fuzzy.FuzzyChoice(
        choices=models.Order.STATUS._db_values)

    item = factory.RelatedFactory(ItemInOrderFactory, 'order')

    class Meta:
        model = 'orders.Order'

    @factory.post_generation
    def amount(self, create, extracted, **kwargs):
        if create:
            self.amount = self._get_amount()
