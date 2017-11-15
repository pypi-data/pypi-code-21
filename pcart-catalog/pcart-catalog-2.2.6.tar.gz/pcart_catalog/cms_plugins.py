from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from .models import CollectionPluginModel, SimilarProductsPluginModel
from .forms import CollectionPluginForm, SimilarProductsPluginForm


class CollectionPluginPublisher(CMSPluginBase):
    model = CollectionPluginModel  # model where plugin data are saved
    form = CollectionPluginForm
    module = _("Catalog")
    name = _("Collection")  # name of the plugin in the interface
    render_template = "catalog/plugins/collection_plugin.html"

    def render(self, context, instance, placeholder):
        from .filtering import ProductsFilterManager
        from .utils import filter_slug_to_tags

        if instance.ajax_load:
            filter_chunks = instance.filter_string
            if filter_chunks and not filter_chunks.startswith('/'):
                filter_chunks = '/' + filter_chunks
            _url = instance.collection.get_absolute_url() + filter_chunks
            if not _url.endswith('/'):
                _url += '/'
            _url += '?view=%s&sort=%s&limit=%s' % (
                instance.template_name, instance.sorting, instance.limit)
            _context = {
                'url': mark_safe(_url),
            }
            _context.update({'parent_context': context})
            _context.update({'instance': instance})
            return _context
        else:
            filter_manager = ProductsFilterManager(
                collection=instance.collection,
                view=instance.template_name,
                sort=instance.sorting,
                limit=instance.limit,
            )
            filter_chunks = instance.filter_string.split('/')
            filter_tags, vendors, prices, normalized_url_chunks, _redirect = filter_slug_to_tags(
                instance.collection, filter_chunks)
            filter_manager.set_filters(filter_tags=filter_tags, vendors=vendors, prices=prices)
            _context = filter_manager.get_context()
            _context.update({'parent_context': context})
            _context.update({'instance': instance})
            return _context


plugin_pool.register_plugin(CollectionPluginPublisher)


class SimilarProductsPluginPublisher(CMSPluginBase):
    model = SimilarProductsPluginModel  # model where plugin data are saved
    form = SimilarProductsPluginForm
    module = _("Catalog")
    name = _("Similar products")  # name of the plugin in the interface
    render_template = "catalog/plugins/similar_products_plugin.html"

    def render(self, context, instance, placeholder):
        from .filtering import ProductsFilterManager
        from .utils import filter_slug_to_tags, normalize_filter_tags

        product = context.get('product')
        _tags_for_filtering = []  # Here we will collect tags for filtering
        for t in instance.tags_or_prefixes:
            if ':' in t:
                # A tag found
                _tags_for_filtering.append(t)
            else:
                # A prefix only, so you should find a related tag for current product
                for i in product.tags:
                    _prefix, _value = i.split(':')
                    if t == _prefix:
                        _tags_for_filtering.append(i)
        _vendors = None
        if instance.vendor_filtering:
            _vendors = [product.vendor]
        _prices = None
        if instance.price_difference_filtering == 'absolute':
            _prices = (
                product.price - instance.price_filtering_value,
                product.price + instance.price_filtering_value,
            )
        elif instance.price_difference_filtering == 'relative':
            _prices = (
                float(int(product.price / instance.price_filtering_value))
                if instance.price_filtering_value != 0 else product.price,
                float(int(product.price * instance.price_filtering_value))
                if instance.price_filtering_value != 0 else product.price,
            )

        if instance.ajax_load:
            _url = instance.collection.get_absolute_url() + '/'.join(
                normalize_filter_tags(
                    instance.collection,
                    _vendors,
                    _prices,
                    _tags_for_filtering,
                )) + '/'
            _url += '?view=%s&sort=%s&limit=%s' % (
                instance.template_name, instance.sorting, instance.limit)
            _context = {
                'url': mark_safe(_url),
            }
            _context.update({'parent_context': context})
            _context.update({'instance': instance})
            return _context
        else:
            filter_manager = ProductsFilterManager(
                collection=instance.collection,
                view=instance.template_name,
                sort=instance.sorting,
                limit=instance.limit,
            )
            filter_manager.set_filters(
                filter_tags=_tags_for_filtering,
                vendors=_vendors,
                prices=_prices,
            )
            _context = filter_manager.get_context()
            _context.update({'parent_context': context})
            _context.update({'instance': instance})
            return _context


plugin_pool.register_plugin(SimilarProductsPluginPublisher)
