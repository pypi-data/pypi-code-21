from django.utils.translation import ugettext_lazy as _
from jinja2.runtime import Context

from shuup.xtheme import TemplatedPlugin

from scatl.services.product.price import get_product_price_max, \
    get_product_price_min


class ScatlPlugin(TemplatedPlugin):
    identifier = 'scatl.catalog'
    name = _('Product catalog plugin')
    template_name = 'scatl/index.jinja'

    def get_context_data(self, context: Context) -> dict:
        data = super().get_context_data(context)
        scatl_data = {
            'product_price_min': int(get_product_price_min()),
            'product_price_max': int(get_product_price_max()),
        }
        return {**data, **scatl_data}
