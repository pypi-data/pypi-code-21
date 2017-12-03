from typing import Optional

from decimal import Decimal

from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.urlresolvers import reverse
from parler_rest.fields import TranslatedFieldsField
from parler_rest.serializers import TranslatableModelSerializer
from rest_framework import serializers
from rest_framework.request import Request
from shuup.core.models import Product, ProductMediaKind, ShopProduct


class ProductSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField()
    price = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    primary_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'translations', 'url', 'primary_image_url', 'price')

    def get_url(self, product: Product) -> str:
        return reverse(
            viewname='shuup:product',
            kwargs={'pk': product.pk, 'slug': product.slug},
        )

    def get_primary_image_url(self, product: Product) -> Optional[str]:
        is_primary_image_exists = product.media.filter(kind=ProductMediaKind.IMAGE).exists()
        if is_primary_image_exists:
            url_relative = product.media.first().file.url
            request = self.context['request'] # type: Request
            return request.build_absolute_uri(url_relative)
        else:
            return static('shuup/front/img/no_image.png')

    def get_price(self, product: Product) -> Decimal:
        shop_product = product.shop_products.first() # type: ShopProduct
        return shop_product.default_price_value
