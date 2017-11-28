from decimal import Decimal
from typing import List, Union, Type

from django.contrib.auth import get_user_model
from django.db.models import Model
from faker import Faker
from shuup.core.models import Category
from shuup.core.models import CategoryStatus
from shuup.core.models import Product
from shuup.core.models import ProductMedia
from shuup.core.models import ProductMediaKind
from shuup.core.models import Shop, PersonContact
from shuup.core.models import ShopProduct
from shuup.core.models import ShopProductVisibility
from shuup.core.models import StockBehavior
from shuup.core.models import Supplier
from shuup.testing.factories import get_default_category
from shuup.testing.factories import get_default_product_type
from shuup.testing.factories import get_default_sales_unit
from shuup.testing.factories import get_default_shop
from shuup.testing.factories import get_default_supplier
from shuup.testing.factories import get_default_tax_class
from shuup.testing.factories import get_random_filer_image

from shuup_testutils.generators import UniqueGen


class ShuupModelsGen:
    def __init__(self):
        self._fake = Faker()
        self._unique_gen = UniqueGen()

    def person_contact(self, user: Type[Model] = None) -> PersonContact:
        contact_user = user or self.user()
        # noinspection PyUnresolvedReferences
        person_contact = PersonContact.objects.create(
            user=contact_user,
            email=contact_user.email,
            first_name=contact_user.first_name,
            last_name=contact_user.last_name,
        )
        return person_contact

    def user(self, user_model: Type[Model] = None, is_superuser: bool = False) -> Type[Model]:
        # TODO: may Fake fail to create a unique username/email?
        user_data = dict(
            username=self._fake.user_name(),
            email=self._fake.email(),
            password=self._fake.password(),
            first_name=self._fake.first_name(),
            last_name=self._fake.last_name(),
            last_login=self._fake.date_time(),
            date_joined=self._fake.date_time(),
        )
        user_model = user_model or get_user_model()
        if is_superuser:
            return user_model.objects.create_superuser(**user_data)
        else:
            return user_model.objects.create(**user_data)

    def products(self, amount: int = 10) -> List[Product]:
        product_list = []
        for _ in range(0, amount):
            product = self.product()
            product_list.append(product)
        return product_list

    # noinspection PyDefaultArgument
    def product(
        self,
        name: str = None,
        shop: Shop = None,
        price: Union[int, float, Decimal, str, None] = Decimal(500),
        primary_category: Category = None,
        categories: List[Category] = [],
        # TODO remove because it isn't required anymore
        product_model = Product,
        supplier: Supplier = None,
    ) -> Product:
        product = product_model(
            type=get_default_product_type(),
            tax_class=get_default_tax_class(),
            sku=self._unique_gen.word(),
            name=name or self._unique_gen.word().title(),
            width=0, height=0, depth=0, net_weight=0, gross_weight=0,
            sales_unit=get_default_sales_unit(),
            stock_behavior=StockBehavior.UNSTOCKED,
        )
        product.full_clean()
        product.save()
        # `full_clean` won't allow a category to be passed as a kwarg above
        product.category = primary_category or get_default_category()
        product.save()

        self._add_image_to_product(product)
        
        shop_instance = shop or get_default_shop()
        # noinspection PyUnresolvedReferences
        shop_product = ShopProduct.objects.create(
            product=product,
            shop=shop_instance,
            default_price=shop_instance.create_price(price) if price else None,
            primary_category=primary_category or get_default_category(),
            visibility=ShopProductVisibility.ALWAYS_VISIBLE,
        )
        shop_product.categories = categories
        shop_product.suppliers.add(supplier or get_default_supplier())
        shop_product.save()

        return product

    def category(self, parent_category: Category = None) -> Category:
        category = Category.objects.create(
            parent=parent_category,
            identifier=self._unique_gen.word(),
            name=self._unique_gen.word().title(),
            slug=self._unique_gen.word(),
            status=CategoryStatus.VISIBLE,
        )
        return category

    def _add_image_to_product(self, product: Product):
        primary_image = ProductMedia.objects.create(
            product=product,
            kind=ProductMediaKind.IMAGE,
            file=get_random_filer_image(),
            enabled=True,
            public=True,
        )
        for shop in Shop.objects.all():
            primary_image.shops.add(shop)
        primary_image.save()
        product.primary_image = primary_image
        product.save()
