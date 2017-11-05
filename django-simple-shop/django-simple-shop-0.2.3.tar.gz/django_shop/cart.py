from decimal import Decimal
from operator import itemgetter

from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from django.utils.timezone import now

from .models import ProductInCart, Product, PackagingBox, Customer, CustomersCart, CartActionLog, CustomersField


class CartModificationError(Exception):
    def __init__(self, message):
        self.message = message


class Cart(object):
    """Объект корзины клиента. Данные о покупках хранятся в сессии на
    стороне сервера
    """

    OLD_CART = '__cart'
    CART_ID = '__cart_id'
    CUSTOMER_ID = '__customer_id'

    def __init__(self, session, need_data=False):
        """
        :type session: django.contrib.sessions.backends.base.SessionBase
        """
        self._need_data = need_data
        self._session = session
        self._cart_id = self._session.get(self.CART_ID)
        self._customer_id = self._session.get(self.CUSTOMER_ID)
        if self._cart_id is not None:
            self._products = self.load_from_db()
        elif self.OLD_CART in self._session:
            self._products = self.load(self._session[self.OLD_CART])
            self.check_create_cart()
            self.save_products()
        else:
            self._products = []

    def check_create_cart(self):
        if self._customer_id is None:
            customer = Customer.objects.create()
            self._customer_id = customer.pk
            self._session[self.CUSTOMER_ID] = self._customer_id

        if self._cart_id is None:
            cart = CustomersCart.objects.create(customer_id=self._customer_id)
            self._cart_id = cart.pk
            self._session[self.CART_ID] = self._cart_id

    def save_products(self):
        self.check_create_cart()

        products_to_insert = []
        for product in self._products:
            products_to_insert.append(
                ProductInCart(cart_id=self._cart_id, product=product['product'], quantity=product['amount'])
            )
        ProductInCart.objects.bulk_create(products_to_insert)

        if self.OLD_CART in self._session:
            del self._session[self.OLD_CART]

    def save(self):
        """Сохранить корзину в сессию"""
        pass

    def load_from_db(self):
        qs = ProductInCart.objects\
            .filter(cart_id=self._cart_id)\
            .annotate(in_stock=Coalesce(Sum('product__entries__quantity'), Value(0)))\
            .select_related('product')
        if self._need_data:
            qs = qs.prefetch_related('product__images', 'product__categories')

        result = []
        to_delete = []
        for pic in qs:
            if pic.in_stock >= pic.quantity:
                result.append({'product': pic.product, 'amount': pic.quantity})
            else:
                to_delete.append(pic.product)
        if to_delete:
            self._delete(to_delete, auto=True)
        return result

    def load(self, basket_data):
        """Загрузить из списка с данными о состоянии корзины структуру,
        описывающую корзину в классе

        :type basket_data: list[(int, float)]

        :rtype: list[dict[django_shop.models.Product, decimal.Decimal]]
        """
        result = []
        product_ids = list(map(itemgetter(0), basket_data))
        qs = Product.objects.filter(pk__in=product_ids)
        if self._need_data:
            qs = qs.prefetch_related('images', 'categories')
        products = {x.id: x for x in qs}
        for product_id, amount in basket_data:
            if product_id not in products:
                continue
            result.append({'product': products[product_id], 'amount': Decimal(amount)})
        return result

    @staticmethod
    def _check_amount(product_obj, amount):
        if not product_obj.is_weight and not float(amount).is_integer():
            raise CartModificationError(
                '{} нельзя купить частично'.format(product_obj)
            )
        if product_obj.is_unlimited:
            return
        if product_obj.in_stock < amount:
            raise CartModificationError(
                'К сожалению, на складе недостаточно товара {} для '
                'добавления в корзину'.format(product_obj)
            )

    def _create(self, product_obj, amount):
        self.check_create_cart()

        action = CartActionLog.ACTION_ADD
        message = "Добавление {}: {} шт".format(product_obj, amount)
        CartActionLog.objects.create(cart_id=self._cart_id, action=action, message=message)

        ProductInCart.objects.update_or_create(cart_id=self._cart_id, product_id=product_obj.pk,
                                               defaults={'quantity': amount})
        self._update_modification_time()

        product = {
            'product': product_obj,
            'amount': amount
        }
        self._products.append(product)

    def _update(self, product_obj, amount):
        self.check_create_cart()

        action = CartActionLog.ACTION_SET
        message = "Установка количества {}: {} шт".format(product_obj, amount)
        CartActionLog.objects.create(cart_id=self._cart_id, action=action, message=message)

        ProductInCart.objects.update_or_create(cart_id=self._cart_id, product_id=product_obj.pk,
                                               defaults={'quantity': amount})
        self._update_modification_time()

    def _delete(self, products, auto=False):
        self.check_create_cart()

        action = CartActionLog.ACTION_DROP if auto else CartActionLog.ACTION_REMOVE
        message = "Удаление продуктов: {}".format(', '.join([str(p) for p in products]))
        CartActionLog.objects.create(cart_id=self._cart_id, action=action, message=message)

        ProductInCart.objects.filter(cart_id=self._cart_id, product_id__in=[p.pk for p in products]).delete()
        self._update_modification_time()

    def _update_modification_time(self):
        CustomersCart.objects.filter(pk=self._cart_id).update(updated=now())

    def _set_field_value(self, ftype, value):
        self.check_create_cart()
        obj = None
        if value:
            obj, _ = CustomersField.objects.update_or_create(customer_id=self._customer_id, type=ftype,
                                                             value=str(value))
        return obj

    def set_ip(self, ip):
        self._set_field_value(CustomersField.TYPE_IP, ip)

    def set_session_id(self, session_id):
        self._set_field_value(CustomersField.TYPE_SESSION_ID, session_id)

    def set_google_id(self, google_id):
        self._set_field_value(CustomersField.TYPE_GOOGLE_ID, google_id)

    def set_yandex_id(self, yandex_id):
        self._set_field_value(CustomersField.TYPE_YANDEX_ID, yandex_id)

    def set_payment_and_delivery(self, payment, delivery):
        self.check_create_cart()
        CustomersCart.objects.filter(pk=self._cart_id).update(payment_method=payment, delivery_type=delivery)

    def set_contacts(self, name, phone, email):
        self.check_create_cart()
        name_obj = self._set_field_value(CustomersField.TYPE_NAME, name)
        phone_obj = self._set_field_value(CustomersField.TYPE_PHONE, phone)
        email_obj = self._set_field_value(CustomersField.TYPE_EMAIL, email)
        kwargs = {}
        if name_obj:
            kwargs['name'] = name_obj
        if phone_obj:
            kwargs['phone'] = phone_obj
        if email_obj:
            kwargs['email'] = email_obj
        if kwargs:
            CustomersCart.objects.filter(pk=self._cart_id).update(**kwargs)

    def set_order(self, order):
        self.check_create_cart()
        CustomersCart.objects.filter(pk=self._cart_id).update(order=order)

    def add(self, product_obj, amount):
        """Добавить указанное количество продукта в корзину

        :type product_obj: django_shop.models.Product
        :type amount: decimal.Decimal
        """
        for product in self._products:
            if product['product'] == product_obj:
                new_amount = product['amount'] + amount
                self._check_amount(product_obj, new_amount)
                self._update(product_obj, amount)
                product['amount'] = new_amount
                break
        else:
            self._check_amount(product_obj, amount)
            self._create(product_obj, amount)

        self.save()

    def remove(self, product_obj):
        """Удалить продукт из корзины

        :type product_obj: django_shop.models.Product
        """
        self._delete([product_obj])

        remove = None
        for num, product in enumerate(self._products):
            if product['product'] == product_obj:
                remove = num
                break

        if remove is not None:
            self._products.pop(remove)

    def set(self, product_obj, amount):
        """Установить количество продукта в корзине

        :type product_obj: django_shop.models.Product
        :type amount: decimal.Decimal
        """
        for product in self._products:
            if product['product'] == product_obj:
                self._check_amount(product_obj, amount)
                self._update(product_obj, amount)
                product['amount'] = amount
                break
        else:
            self._check_amount(product_obj, amount)
            self._create(product_obj, amount)

        self.save()

    def get_amount(self, product_obj):
        """Узнать количество продукта в корзине

        :type product_obj: django_shop.models.Product
        """
        for product in self._products:
            if product['product'] == product_obj:
                return product['amount']
        return 0

    def clean(self):
        """Очистить корзину"""
        del self._session[self.CART_ID]
        self._products = []
        self.save()

    @property
    def price(self):
        """Цена всех продуктов в корзине"""
        return sum(p['product'].price * p['amount'] for p in self._products)

    @property
    def weight(self):
        """Вес всех продуктов в корзине"""
        return sum(p['product'].weight * p['amount'] for p in self._products)

    @property
    def measures(self):
        """Измерения прямоуголной коробки, в которую поместятся все продукты в
        корзине
        """
        return PackagingBox.get_measures_for_products(
            p['product'] for p in self._products)

    @property
    def items_num(self):
        """Количество продуктов в корзине"""
        return len(self._products)

    @property
    def is_empty(self):
        return self.items_num == 0

    def __iter__(self):
        return (
            (p['product'], p['amount'],
             p['product'].price * Decimal(p['amount'])) for p in self._products
        )

    def __bool__(self):
        return bool(self._products)
