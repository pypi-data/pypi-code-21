from django.utils.translation import ugettext as _
# from django.utils.safestring import mark_safe
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from .models import ProductFinderFormPluginModel
from .forms import ProductFinderFormPluginForm


class ProductFinderFormPluginPublisher(CMSPluginBase):
    model = ProductFinderFormPluginModel  # model where plugin data are saved
    form = ProductFinderFormPluginForm
    module = _("Product finder")
    name = _("Product finder form")  # name of the plugin in the interface
    render_template = "productfinder/plugins/form_plugin.html"

    def render(self, context, instance, placeholder):
        _context = {'instance': instance}
        return _context


plugin_pool.register_plugin(ProductFinderFormPluginPublisher)
