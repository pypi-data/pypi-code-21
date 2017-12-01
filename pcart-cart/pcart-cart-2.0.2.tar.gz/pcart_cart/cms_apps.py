from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _


class CartApphook(CMSApp):
    app_name = "pcart_cart"
    name = _("Cart")

    def get_urls(self, page=None, language=None, **kwargs):
        return ["pcart_cart.urls"]

apphook_pool.register(CartApphook)