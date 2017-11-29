from django.utils.translation import ugettext_lazy as _
from cms.toolbar_pool import toolbar_pool
from cms.toolbar_base import CMSToolbar
from cms.utils.urlutils import admin_reverse
from .models import Product, Collection


@toolbar_pool.register
class CollectionToolbar(CMSToolbar):
    supported_apps = (
        'pcart_catalog',
    )
    watch_models = [Collection,]

    def populate(self):
        if not self.is_current_app:
            return

        menu = self.toolbar.get_or_create_menu('collection-app', _('Collection'))

        menu.add_sideframe_item(
            name=_('Collections list'),
            url=admin_reverse('pcart_catalog_collection_changelist'),
        )

        menu.add_modal_item(
            name=_('Add new collection'),
            url=admin_reverse('pcart_catalog_collection_add'),
        )
        # menu.add_modal_item(
        #     name=_('Edit collection'),
        #     url=admin_reverse('pcart_catalog_collection_change', [self.]),
        # )


@toolbar_pool.register
class ProductToolbar(CMSToolbar):
    supported_apps = (
        'pcart_catalog',
    )
    watch_models = [Product,]

    def populate(self):
        if not self.is_current_app:
            return

        menu = self.toolbar.get_or_create_menu('product-app', _('Product'))

        menu.add_sideframe_item(
            name=_('Products list'),
            url=admin_reverse('pcart_catalog_product_changelist'),
        )

        current_product_id = getattr(self.request, 'productid', None)
        if current_product_id:
            menu.add_modal_item(
                name=_('Edit product'),
                url=admin_reverse('pcart_catalog_product_change', args=(current_product_id,)),
                active=True,
            )

        menu.add_modal_item(
            name=_('Add new product'),
            url=admin_reverse('pcart_catalog_product_add'),
        )
