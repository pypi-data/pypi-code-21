from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _
from .cms_menus import CollectionMenu


class CollectionApphook(CMSApp):
    app_name = "pcart_collection"
    name = _("Product collection")
    menus = [CollectionMenu]

    def get_urls(self, page=None, language=None, **kwargs):
        return ["pcart_catalog.urls_collection"]

apphook_pool.register(CollectionApphook)


class ProductApphook(CMSApp):
    app_name = "pcart_product"
    name = _("Product detail")

    def get_urls(self, page=None, language=None, **kwargs):
        return ["pcart_catalog.urls_product"]

apphook_pool.register(ProductApphook)

