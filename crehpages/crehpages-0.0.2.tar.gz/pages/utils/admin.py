from django.contrib import admin
from django.db.models.loading import get_model

from pages.utils import constants


class ProductInline(admin.TabularInline):
    extra = 1


def get_page_inline_form():
    products = constants.PAGE_PRODUCTS
    for product in products:
        model = get_model(product[0], product[1])
    return ProductInline