from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.urls import reverse, NoReverseMatch
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
# from django.utils.functional import lazy
from django.core.cache import cache
from adminsortable.fields import SortableForeignKey
from adminsortable.models import SortableMixin
from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager
from mptt.querysets import TreeQuerySet
from cms.models import CMSPlugin
from cms.models.fields import PlaceholderField
from djangocms_text_ckeditor.fields import HTMLField
from parler.models import TranslatableModel, TranslatedFields
from parler.managers import TranslatableManager, TranslatableQuerySet
import uuid

from typing import List, Tuple, Union, Optional, Dict


MAX_TAG_LENGTH = 30


class ProductType(TranslatableModel):
    """
    Describes a nature of any product from the catalog. Is using as a container for a properties list.
    The `title` value must be unique across the database.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    translations = TranslatedFields(
        title=models.CharField(_('Title'), max_length=255, unique=True),
        # SEO (you can store templates here)
        # Usable for setup SEO templates for all products of the particular type.
        page_title=models.CharField(_('Page title'), max_length=255, blank=True),
        meta_description=models.TextField(_('Meta description'), blank=True),
        meta_keywords=models.TextField(_('Meta keywords'), blank=True),
        meta_text=models.TextField(_('Meta text'), blank=True),
    )

    # Useful default values
    default_quantity_for_purchase = models.PositiveIntegerField(
        _('Default quantity for purchase'), default=1)

    # CMS placeholders
    primary_placeholder = PlaceholderField(
        'primary_product_type_placeholder', related_name='product_type_primary')
    secondary_placeholder = PlaceholderField(
        'secondary_product_type_placeholder', related_name='product_type_secondary')

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Product type')
        verbose_name_plural = _('Product types')
        # ordering = ['title']

    def __str__(self) -> str:
        return self.title

    def get_properties_fields(self, initial_values: Optional[Dict] = None, for_variants: bool = False) -> List[Tuple]:
        """
        Returns the list of tuples with some data useful for the product managing forms for admin interface.
        """
        from django import forms

        if initial_values is None:
            initial_values = dict()  # A trick for prevent using the mutable value as default

        if for_variants:
            properties = self.properties.filter(for_variants=True)
        else:
            properties = self.properties.all()
        result = [
            (
                'property_%s' % i,
                p.title,
                forms.CharField(label=p.title, initial=initial_values.get(p.title) or p.default_value, required=False),
            ) for i, p in enumerate(properties)]
        return result

    def get_visible_properties(self):
        _result = self.properties.exclude(hidden=True)
        return _result


class ProductTypeProperty(SortableMixin):
    """
    Represents a product property related to the specified product type.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_('Title'), max_length=255)

    default_value = models.CharField(_('Default value'), max_length=255, blank=True)
    tag_prefix = models.CharField(_('Tag prefix'), max_length=10, blank=True)

    use_in_filters = models.BooleanField(_('Use in filters'), default=False)
    for_variants = models.BooleanField(_('For variants'), default=False)

    hidden = models.BooleanField(
        _('Hidden'), default=False,
        help_text=_('Useful for hide some product specified information from a web page.'))

    product_type = SortableForeignKey(ProductType, verbose_name=_('Product type'), related_name='properties')

    position = models.PositiveIntegerField(_('Position'), default=0, editable=False, db_index=True)

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Product type property')
        verbose_name_plural = _('Product type properties')
        ordering = ['position']

    def __str__(self) -> str:
        return self.title


# Listen for signals for ProductTypeProperty

@receiver(pre_save, sender=ProductTypeProperty)
def product_type_pre_save_listener(sender, instance: 'ProductTypeProperty', **kwargs):
    _updated = False
    if instance.pk:
        from .tasks import rename_property_name, update_product_tags
        product_type_id = instance.product_type_id
        try:
            ptp = ProductTypeProperty.objects.get(pk=instance.pk)
            old_title = ptp.title
            new_title = instance.title
            if old_title != new_title:
                rename_property_name.delay(product_type_id, old_title, new_title)
                _updated = True
            if not _updated and ptp.tag_prefix != instance.tag_prefix:
                update_product_tags.delay(product_type_id, new_title)
        except ProductTypeProperty.DoesNotExist:
            pass


def generate_collection_image_filename(instance: 'Collection', filename: str) -> str:
    ext = filename.split('.')[-1]
    url = 'images/collections/%s/%s.%s' % (instance.id, str(uuid.uuid4()).replace('-', ''), ext)
    return url


class CollectionQuerySet(TranslatableQuerySet, TreeQuerySet):
    pass
    # Optional: make sure the Django 1.7 way of creating managers works.
    # def as_manager(cls):
    #     manager = CategoryManager.from_queryset(cls)()
    #     manager._built_with_as_manager = True
    #     return manager
    # as_manager.queryset_only = True
    # as_manager = classmethod(as_manager)


class CollectionManager(TreeManager, TranslatableManager):
    queryset_class = CollectionQuerySet

    def get_queryset(self):
        # This is the safest way to combine both get_queryset() calls
        # supporting all Django versions and MPTT 0.7.x versions
        return self.queryset_class(self.model, using=self._db).order_by(self.tree_id_attr, self.left_attr)


class Collection(MPTTModel, TranslatableModel):
    """
    Describes a page on the site with a list of products and such features like filtering, sorting and
    support of multiple templates.
    """

    DEFAULT_URL_FILTER_RULES = '''VENDOR
PRICE'''
    PRODUCTS_SELECTION_CHOICES = (
        ('manual', _('Manual')),
        ('automatic', _('Automatic')),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey(
        Site, verbose_name=_('Site'), related_name='collections', on_delete=models.PROTECT)
    slug = models.SlugField(_('Slug'), unique=True)
    parent = TreeForeignKey(
        'self', null=True, blank=True, related_name='children', db_index=True,
        verbose_name=_('Parent'),
    )

    image = models.ImageField(_('Image'), null=True, blank=True, upload_to=generate_collection_image_filename)

    translations = TranslatedFields(
        title=models.CharField(_('Title'), max_length=255),
        description=HTMLField(_('Description'), blank=True),
        # SEO
        page_title=models.CharField(_('Page title'), max_length=255, blank=True),
        meta_description=models.TextField(_('Meta description'), blank=True),
        meta_keywords=models.TextField(_('Meta keywords'), blank=True),
        meta_text=models.TextField(_('Meta text'), blank=True),
    )

    # URL filter rules
    custom_url_filter_rules = models.BooleanField(_('Custom URL filter rules'), default=False)
    url_filter_rules = models.TextField(
        _('URL filter rules'), blank=True, default=DEFAULT_URL_FILTER_RULES,
        help_text=_('Use separate lines for different rules. See documentation for details.')
    )

    # Filters visibility
    show_vendor_filter = models.BooleanField(_('Show vendor filter'), default=True)
    show_properties_filters = models.BooleanField(_('Show properties filters'), default=True)
    exclude_properties_filters = ArrayField(
        models.CharField(max_length=70),
        verbose_name=_('Exclude properties filters'), default=list, blank=True,
        help_text=_('Comma separated list of properties labels which you want to exclude from filters.'),
    )
    show_price_filter = models.BooleanField(_('Show price filter'), default=True)

    # Product selection mode
    products_selection = models.CharField(
        _('Products selection'), max_length=30, default='manual',
        choices=PRODUCTS_SELECTION_CHOICES,
        help_text=_('Use Automatic mode if you want to select products based on conditions.'),
    )

    # The list of conditions for automated collections
    condition_vendors = models.ManyToManyField(
        'Vendor', verbose_name=_('Vendors'), blank=True, related_name='auto_collections')
    condition_product_types = models.ManyToManyField(
        'ProductType', verbose_name=_('Product types'), blank=True, related_name='auto_collections')
    condition_min_price = models.DecimalField(_('Min price'), max_digits=10, decimal_places=2, default=0.00)
    condition_max_price = models.DecimalField(_('Max price'), max_digits=10, decimal_places=2, default=0.00)
    mandatory_tags = ArrayField(
        models.CharField(max_length=MAX_TAG_LENGTH), verbose_name=_('Mandatory tags'),
        default=list, blank=True,
    )
    optional_tags = ArrayField(
        models.CharField(max_length=MAX_TAG_LENGTH), verbose_name=_('Optional tags'),
        default=list, blank=True,
    )

    # Trigger
    trigger_regex = models.CharField(
        _('Trigger regex'), max_length=150, default='', blank=True,
        help_text=_('Regular expression for checking the optional url trigger. Usable for some 3rd party modules.'),
    )
    trigger_module = models.CharField(_('Trigger module'), max_length=70, default='', blank=True)

    # Publication
    published = models.BooleanField(_('Published'), default=True)
    virtual = models.BooleanField(_('Virtual'), default=False)
    badged = models.BooleanField(_('Badged'), default=False)

    # CMS placeholders
    primary_placeholder = PlaceholderField(
        'primary_collection_placeholder', related_name='collection_primary')
    secondary_placeholder = PlaceholderField(
        'secondary_collection_placeholder', related_name='collection_secondary')
    extra_placeholder = PlaceholderField(
        'secondary_collection_placeholder', related_name='collection_extra')

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    objects = CollectionManager()

    class Meta:
        verbose_name = _('Collection')
        verbose_name_plural = _('Collections')

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        try:
            return reverse('pcart_collection:product-list-for-collection', args=[self.slug])
        except NoReverseMatch:
            return '#no-page-for-collection-app'

    def as_dict(self) -> Dict:
        result = {
            'id': self.id,
            'title': self.title,
            'site': {'domain': self.site.domain, 'name': self.site.name},
            'slug': self.slug,
            'parent': self.parent_id,
            'description': self.description,
            'page_title': self.page_title,
            'published': self.published,
            'added': self.added,
            'changed': self.changed,
            'url': self.get_absolute_url(),
        }
        return result

    def get_product_types(self):
        """ Returns a set of unique ProductType instances available for the collection."""
        if self.products_selection == 'manual':
            return ProductType.objects.filter(products__collections=self).distinct()
        elif self.products_selection == 'automatic':
            return self.condition_product_types.all()

    def get_url_filter_rules(self) -> str:
        """ Returns URL filter rules"""
        if self.custom_url_filter_rules:
            return self.url_filter_rules
        else:
            _cache_key = 'url-filter-rules-%s' % self.pk
            result = cache.get(_cache_key)
            if result:
                return result

            _product_types = self.get_product_types()
            _filter_rules = []
            if self.show_vendor_filter:
                _filter_rules.append('VENDOR')
            if self.show_properties_filters:
                for p_type in _product_types:
                    f_props = p_type.properties.filter(use_in_filters=True)
                    for prop in f_props:
                        if prop.title not in self.exclude_properties_filters:
                            _filter_rules.append('TAG/+%s/VALUE ONLY IGNORE DASH' % prop.tag_prefix)
            if self.show_price_filter:
                _filter_rules.append('PRICE')
            result = '\n'.join(_filter_rules)
            cache.set(_cache_key, result, 60*15)    # save for 15 min
            return result


class ProductStatus(TranslatableModel):
    """
    Represents a product status model.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # title = models.CharField(_('Title'), max_length=255, unique=True)

    translations = TranslatedFields(
        title=models.CharField(_('Title'), max_length=255, unique=True)
    )

    show_buy_button = models.BooleanField(_('Show buy button'), default=True)
    is_visible = models.BooleanField(_('Is visible'), default=True)
    is_searchable = models.BooleanField(_('Is searchable'), default=True)

    weight = models.PositiveIntegerField(_('Weight'), default=0)

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Product status')
        verbose_name_plural = _('Product statuses')
        ordering = ['-weight']

    def __str__(self) -> str:
        return self.title

    def as_dict(self) -> Dict:
        result = {
            'id': self.id,
            'title': self.title,
            'show_buy_button': self.show_buy_button,
            'is_visible': self.is_visible,
            'is_searchable': self.is_searchable,
            'weight': self.weight,
        }
        return result


def generate_vendor_image_filename(instance: 'Vendor', filename: str) -> str:
    ext = filename.split('.')[-1]
    url = 'images/vendors/%s/%s.%s' % (instance.id, str(uuid.uuid4()).replace('-', ''), ext)
    return url


class Vendor(TranslatableModel):
    """
    Represents a product vendor.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(_('Slug'), max_length=255, unique=True)
    image = models.ImageField(_('Image'), null=True, blank=True, upload_to=generate_vendor_image_filename)

    translations = TranslatedFields(
        title=models.CharField(_('Title'), max_length=255, unique=True),
        description=HTMLField(_('Description'), blank=True),
    )

    class Meta:
        verbose_name = _('Vendor')
        verbose_name_plural = _('Vendors')

    def __str__(self) -> str:
        return self.title

    def as_dict(self) -> dict:
        result = {
            'id': self.id,
            'title': self.title,
        }
        return result


class Product(TranslatableModel):
    """
    Represents a product.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(_('Slug'), max_length=255, unique=True)
    external_id = models.CharField(
        _('External ID'), default='', blank=True, max_length=255, db_index=True)

    translations = TranslatedFields(
        title=models.CharField(_('Title'), max_length=255),
        description=HTMLField(_('Description'), blank=True),
        # SEO
        page_title=models.CharField(_('Page title'), max_length=255, blank=True),
        meta_description=models.TextField(_('Meta description'), blank=True),
        meta_keywords=models.TextField(_('Meta keywords'), blank=True),
        meta_text=models.TextField(_('Meta text'), blank=True),
    )

    vendor = models.ForeignKey(
        Vendor, verbose_name=_('Vendor'), related_name='products', null=True, blank=True, on_delete=models.SET_NULL)
    product_type = models.ForeignKey(
        ProductType, verbose_name=_('Product type'), related_name='products', on_delete=models.CASCADE)
    collections = models.ManyToManyField(
        Collection, verbose_name=_('Collections'), related_name='products', blank=True,
        help_text=_('Add this product to a collection so it\'s easy to find in your store.'),
    )

    tags = ArrayField(
        models.CharField(max_length=MAX_TAG_LENGTH),
        verbose_name=_('Tags'),
        blank=True,
        default=list,
    )
    properties = JSONField(_('Properties'), default=dict, blank=True)

    sku = models.CharField(_('SKU (Stock Keeping Unit)'), blank=True, max_length=100)
    barcode = models.CharField(_('Barcode (ISBN, UPC, GTIN, etc.)'), blank=True, max_length=100)

    status = models.ForeignKey(
        ProductStatus, verbose_name=_('Status'), related_name='products', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(_('Quantity'), default=None, null=True, blank=True)

    price = models.DecimalField(_('Price'), max_digits=10, decimal_places=2, default=0.00)
    compare_at_price = models.DecimalField(_('Compare at price'), max_digits=10, decimal_places=2, default=0.00)
    price_varies = models.BooleanField(_('Price varies'), default=False)

    # Set automatically with stored procedure. For read only access.
    max_variant_price = models.DecimalField(_('Max variant price'), max_digits=10, decimal_places=2, default=0.00)
    min_variant_price = models.DecimalField(_('Min variant price'), max_digits=10, decimal_places=2, default=0.00)
    variants_count = models.PositiveIntegerField(_('Variants count'), default=0)

    weight = models.FloatField(
        _('Weight (kg)'), default=0.0, help_text=_('Used to calculate shipping rates at checkout.'))

    # Some extra attributes
    rank_1 = models.FloatField(_('Rank 1'), default=0.0)
    rank_2 = models.FloatField(_('Rank 2'), default=0.0)
    rank_3 = models.FloatField(_('Rank 3'), default=0.0)

    extra_int_1 = models.IntegerField(_('Extra int 1'), default=0)
    extra_int_2 = models.IntegerField(_('Extra int 2'), default=0)
    extra_float_1 = models.FloatField(_('Extra float 1'), default=0.0)
    extra_float_2 = models.FloatField(_('Extra float 2'), default=0.0)

    extra_price_1 = models.DecimalField(_('Extra price 1'), max_digits=10, decimal_places=2, default=0.00)
    extra_price_2 = models.DecimalField(_('Extra price 2'), max_digits=10, decimal_places=2, default=0.00)
    extra_price_3 = models.DecimalField(_('Extra price 3'), max_digits=10, decimal_places=2, default=0.00)

    extra_text_1 = models.TextField(_('Extra text 1'), default='', blank=True)
    extra_text_2 = models.TextField(_('Extra text 2'), default='', blank=True)

    extra_data = JSONField(_('Extra data'), default=dict, blank=True)
    extra_id_1 = models.CharField(_('Extra ID 1'), default='', blank=True, max_length=255, db_index=True)
    extra_id_2 = models.CharField(_('Extra ID 2'), default='', blank=True, max_length=255, db_index=True)

    published = models.BooleanField(_('Published'), default=True)

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['id']

    def __str__(self) -> str:
        return self.title

    @staticmethod
    def type() -> str:
        return 'product'

    def get_absolute_url(self) -> str:
        try:
            return reverse('pcart_product:product-detail', args=[self.slug])
        except NoReverseMatch:
            return '#no-page-for-product-app'

    def get_properties_fields(self, initial_values: Optional[Dict] = None, for_variants: bool = False) -> List[Tuple]:
        """
        Returns properties list for generate product form for admin.
        """
        return self.product_type.get_properties_fields(
            initial_values=self.properties if initial_values is None else initial_values,
            for_variants=for_variants)

    def has_variants(self) -> bool:
        """
        Returns `True` if the product has one or more variants.
        """
        return self.variants_count > 0

    def get_image(self) -> 'ProductImage':
        """
        Returns a first available image for the product.
        """
        return self.images.first()

    def available(self) -> bool:
        """
        Returns `True` if the product does not have variants, positive price and corresponding status.
        """
        return self.variants_count == 0 and self.price > 0 and self.status.show_buy_button

    def as_dict(self) -> Dict:
        result = {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'description': self.description,
            'page_title': self.page_title,
            'tags': self.tags,
            'properties': self.properties,
            'sku': self.sku,
            'barcode': self.barcode,
            'status': self.status.as_dict(),
            'price': self.price,
            'price_varies': self.price_varies,
            'compare_at_price': self.compare_at_price,
            'max_variant_price': self.max_variant_price,
            'min_variant_price': self.min_variant_price,
            'variants_count': self.variants_count,
            'weight': self.weight,
            'published': self.published,
            'url': self.get_absolute_url(),
        }
        return result

    def get_page_title(self) -> str:
        """
        Returns a product page title.
        """
        return self.page_title or self.title

    def get_collections(self, exclude_virtual=False, exclude_badged=False, badged_only=False):
        from django.db.models import Q
        manual_collections_ids = self.collections.values_list('id', flat=True)
        _result = Collection.objects.filter(
            Q(pk__in=manual_collections_ids) | (
                Q(products_selection='automatic') &
                (Q(condition_product_types=None) | Q(condition_product_types=self.product_type)) &
                (Q(condition_vendors=None) | Q(condition_vendors=self.vendor)) &
                (Q(condition_min_price=0.0) | Q(condition_min_price__lte=self.price)) &
                (Q(condition_max_price=0.0) | Q(condition_max_price__gte=self.price)) &
                (Q(mandatory_tags=[]) | Q(mandatory_tags__contained_by=self.tags)) &
                (Q(optional_tags=[]) | Q(optional_tags__overlap=self.tags))
            )
        )
        if exclude_virtual:
            _result = _result.exclude(virtual=True)
        if exclude_badged:
            _result = _result.exclude(badged=True)
        if badged_only:
            _result = _result.exclude(badged=False)
        _result = _result.prefetch_related('translations')
        return _result

    def get_badged_collections(self):
        return self.get_collections(badged_only=True)

    def get_breadcrumb_collections(self):
        return self.get_collections(exclude_virtual=True, exclude_badged=True)

    def get_collection(self):
        return self.get_collections(exclude_virtual=True, exclude_badged=True).first()


@receiver(post_save, sender=Product)
def product_post_save_listener(sender, instance: 'Product', **kwargs):
    from .utils import filter_non_numeric_tags
    tagset = instance.tags
    values = filter_non_numeric_tags(tagset)
    PropertyValueSlug.objects.add_values(values)


class ProductVariant(TranslatableModel):
    """
    Represents a product variant.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(_('Slug'), unique=False, max_length=255)
    external_id = models.CharField(
        _('External ID'), default='', blank=True, max_length=255, db_index=True)

    translations = TranslatedFields(
        title=models.CharField(_('Title'), max_length=255)
    )

    product = models.ForeignKey(
        Product, verbose_name=_('Product'), related_name='variants', on_delete=models.CASCADE)

    tags = ArrayField(
        models.CharField(max_length=MAX_TAG_LENGTH),
        verbose_name=_('Tags'),
        blank=True,
        default=list,
    )
    properties = JSONField(_('Properties'), default=dict, blank=True)

    sku = models.CharField(_('SKU (Stock Keeping Unit)'), blank=True, max_length=100)
    barcode = models.CharField(_('Barcode (ISBN, UPC, GTIN, etc.)'), blank=True, max_length=100)

    status = models.ForeignKey(ProductStatus, verbose_name=_('Status'), related_name='variants')
    quantity = models.PositiveIntegerField(_('Quantity'), default=None, null=True, blank=True)

    price = models.DecimalField(_('Price'), max_digits=10, decimal_places=2, default=0.00)
    compare_at_price = models.DecimalField(_('Compare at price'), max_digits=10, decimal_places=2, default=0.00)
    price_varies = models.BooleanField(_('Price varies'), default=False)

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Product variant')
        verbose_name_plural = _('Product variants')
        ordering = ['id']
        unique_together = ['product', 'slug']

    def __str__(self) -> str:
        return self.title

    @staticmethod
    def type() -> str:
        return 'variant'

    def get_absolute_url(self) -> str:
        try:
            return reverse('pcart_product:product-variant-detail', args=[self.product.slug, self.slug])
        except NoReverseMatch:
            return '#no-page-for-product-app'

    def get_properties_fields(self, initial_values: Optional[Dict] = None) -> List[Tuple]:
        return self.product.product_type.get_properties_fields(
            initial_values=self.properties if initial_values is None else initial_values,
            for_variants=True)

    def get_image(self) -> 'ProductImage':
        return self.product.get_image()

    def weight(self) -> float:
        return self.product.weight

    def available(self) -> bool:
        return self.price > 0 and self.status.show_buy_button


def generate_product_image_filename(instance: 'ProductImage', filename: str) -> str:
    ext = filename.split('.')[-1]
    url = 'images/products/%s/%s.%s' % (instance.product.id, str(uuid.uuid4()).replace('-', ''), ext)
    return url


class ProductImage(SortableMixin, TranslatableModel):
    """
    Represents a product image.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    translations = TranslatedFields(
        title=models.CharField(_('Title'), max_length=255, default='', blank=True)
    )

    product = SortableForeignKey(
        Product, verbose_name=_('Product'), related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(_('Image'), null=True, blank=True, upload_to=generate_product_image_filename)
    html_snippet = models.TextField(_('HTML snippet'), default='', blank=True)

    tags = ArrayField(
        models.CharField(max_length=MAX_TAG_LENGTH),
        verbose_name=_('Tags'),
        blank=True,
        default=list,
    )

    download_link = models.CharField(_('Download link'), max_length=300, default='', blank=True)
    downloaded = models.BooleanField(_('Downloaded'), default=False)

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    position = models.PositiveIntegerField(_('Position'), default=0, editable=False, db_index=True)

    class Meta:
        verbose_name = _('Product image')
        verbose_name_plural = _('Product images')
        ordering = ['position']

    def __str__(self) -> str:
        return self.title or self.product.title

    def download_product_image(self, save: bool = False):
        from django.core.files import File
        from ftplib import FTP
        from io import BytesIO
        import urllib.parse
        import os
        _changed = False
        o = urllib.parse.urlparse(self.download_link)

        if self.downloaded is False:
            if o.scheme in ['http', 'https']:
                # Download an image via HTTP
                local_filename, headers = urllib.request.urlretrieve(self.download_link)
                self.image.save(
                    os.path.basename(o.path),
                    File(open(local_filename, 'rb')),
                    save=False,
                )
                self.downloaded = True
                _changed = True
            elif o.scheme == 'ftp':
                # Download an image via FTP
                _ftp_sources = getattr(settings, 'PCART_FTP_IMAGE_SOURCES', {})
                _credentials = _ftp_sources.get(o.netloc)
                with FTP(o.netloc) as ftp:
                    if _credentials:
                        ftp.login(_credentials.get('user'), _credentials.get('password'))
                    else:
                        ftp.login()
                    ftp.getwelcome()
                    r = BytesIO()
                    ftp.retrbinary('RETR ~/%s' % o.path, r.write)
                    r.seek(0)

                    self.image.save(
                        os.path.basename(o.path),
                        File(r),
                        save=False,
                    )
                    self.downloaded = True
                    _changed = True

        if save and _changed:
            self.save()

    def save(self, *args, **kwargs):
        # Force image download if the link is specified
        if self.downloaded is False and self.download_link:
            self.download_product_image(save=False)
        super(ProductImage, self).save(*args, **kwargs)


@receiver(pre_save, sender=ProductImage)
def product_image_pre_save_listener(sender, instance: 'ProductImage', **kwargs):
    if instance.pk:
        try:
            p_im = ProductImage.objects.get(pk=instance.pk)
            if p_im.image and p_im.image != instance.image:
                p_im.image.delete(save=False)
        except ProductImage.DoesNotExist:
            pass


@receiver(post_delete, sender=ProductImage)
def product_image_post_delete_listener(sender, instance: 'ProductImage', **kwargs):
    if instance.image:
        instance.image.delete(save=False)


class PropertyValueSlugManager(models.Manager):
    """
    Queryset manager for `PropertyValueSlug` model. Filtering system is using it for autogeneration URL chunks
    for filtered colelction URLs.
    """
    def generate_unique_slug(self, value: str) -> str:
        """Returns a unique slug available for use for property value."""
        from pcart_core.utils import get_unique_slug
        slug = get_unique_slug(value, self.model)
        return slug

    def add_values(self, values: Optional[List] = None):
        values = [] if values is None else list(set(values))
        existing_values = self.filter(value__in=values).values_list('value', flat=True)
        for v in values:
            if v not in existing_values:
                slug = self.generate_unique_slug(v)
                item = self.model(value=v, slug=slug)
                item.save(using=self._db)

    def update_data(self, products=None):
        from .utils import get_unique_tagset, filter_non_numeric_tags
        values = filter_non_numeric_tags(get_unique_tagset(products))
        self.add_values(values)


class PropertyValueSlug(models.Model):
    """
    Represents property value slug. Such slugs are using by filtering system for making possible to autogenerate
    filtered collection URLs for property values which cannot be using as URL chunks without properly encoding.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    value = models.CharField(_('Value'), max_length=255, unique=True)
    slug = models.SlugField(_('Slug'), max_length=255, unique=True)

    objects = PropertyValueSlugManager()

    class Meta:
        verbose_name = _('Property value slug')
        verbose_name_plural = _('Property values slugs')
        ordering = ['value']

    def __str__(self) -> str:
        return self.value


class PriceAggregationProfile(models.Model):
    """ Represents a price aggregation profile. It helps to generate `.xml` file for
    price aggregators like Hotline or PriceUA.
    """
    PRICE_XML_DIRECTORY = 'prices'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_('Title'), max_length=255, unique=True)
    site = models.ForeignKey(
        Site, verbose_name=_('Site'), related_name='price_aggregation_profiles', on_delete=models.PROTECT)
    account_id = models.CharField(
        _('Account ID'), max_length=150, blank=True,
        help_text=_('The account ID on the particular price aggregator.')
    )
    language = models.CharField(_('Language'), max_length=10)
    file_name = models.CharField(
        _('File name'), max_length=150, unique=True,
        help_text=_('File name, like prices.xml for example.'),
    )
    template_name = models.CharField(_('Template name'), default='', blank=True, max_length=100)

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Price aggregation profile')
        verbose_name_plural = _('Price aggregation profiles')
        ordering = ['title']

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        url = '%s%s/%s' % (settings.MEDIA_URL, self.PRICE_XML_DIRECTORY, self.file_name)

    def generate(self):
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        from django.template.loader import render_to_string
        from django.utils import translation
        from .settings import PCART_PRICE_AGGREGATION_TEMPLATES

        language_code = settings.LANGUAGE_CODE
        translation.activate(language_code)
        collections = Collection.objects.language(language_code) \
            .filter(published=True).exclude(virtual=True)

        products = Product.objects.language(language_code).filter(published=True)
        products = products.prefetch_related('translations')
        products = products.prefetch_related('vendor')
        products = products.prefetch_related('vendor__translations')
        products = products.prefetch_related('status')
        products = products.prefetch_related('images')
        products = products.prefetch_related('collections')
        products = products.prefetch_related('product_type')

        context = {
            'site': self.site,
            'protocol': 'https' if getattr(settings, 'USE_HTTPS', False) else 'http',
            'account_id': self.account_id,
            'collections': collections,
            'currency_code': settings.PCART_DEFAULT_CURRENCY.upper(),
            'products': products,
        }
        content = render_to_string(
            PCART_PRICE_AGGREGATION_TEMPLATES[self.template_name]['template'], context)

        if default_storage.exists(self.file_name):
            default_storage.delete(self.file_name)
        path = default_storage.save(self.file_name, ContentFile(content))
        return path

# DjangoCMS plugins


class CollectionPluginModel(CMSPlugin):
    """ Represents a plugin with a products from the specified collection.
    """
    collection = TreeForeignKey(Collection, verbose_name=_('Collection'))
    show_title = models.BooleanField(_('Show title'), default=True)
    title = models.CharField(
        _('Title'), max_length=255, default='', blank=True,
        help_text=_('Optional. If not set the collection title will be used.')
    )
    filter_string = models.CharField(
        _('Filter string'), default='', blank=True, max_length=255,
        help_text=_('Use the list of filter chunks separated with / and ; characters.')
    )
    sorting = models.CharField(_('Sorting'), default='', blank=True, max_length=100)
    limit = models.PositiveIntegerField(_('Limit'), default=6)
    template_name = models.CharField(_('Template name'), default='', blank=True, max_length=100)
    data = JSONField(
        _('Data'), default=dict, blank=True,
        help_text=_('Optional. Some templates may support additional options for conditional rendering.'),
    )
    ajax_load = models.BooleanField(_('AJAX load'), default=False)

    def __init__(self, *args, **kwargs):
        super(CollectionPluginModel, self).__init__(*args, **kwargs)

    def __str__(self) -> str:
        return str(self.collection)


class SimilarProductsPluginModel(CMSPlugin):
    """
    Represents a plugin with a list of products with set of specified tags related to the product
    which page plugin inserted into.
    """
    PRICE_FILTERING_CHOICES = (
        ('', _('Do not filter')),
        ('absolute', _('Absolute difference')),
        ('relative', _('Relative difference')),
    )

    collection = TreeForeignKey(Collection, verbose_name=_('Collection'))
    show_title = models.BooleanField(_('Show title'), default=True)
    title = models.CharField(
        _('Title'), max_length=255, default='', blank=True,
        help_text=_('Optional. If not set the collection title will be used.')
    )
    tags_or_prefixes = ArrayField(
        models.CharField(max_length=MAX_TAG_LENGTH),
        verbose_name=_('Tags or prefixes'),
        blank=True,
        default=list,
        help_text=_('You can specify like full tag as `prefix:value` but also `prefix` only.')
    )
    vendor_filtering = models.BooleanField(_('Vendor filtering'), default=False)
    price_difference_filtering = models.CharField(
        _('Price difference filtering'), default='', blank=True,
        max_length=30,
        choices=PRICE_FILTERING_CHOICES)
    price_filtering_value = models.DecimalField(
        _('Price filtering value'), max_digits=10, decimal_places=2, default=0.00)

    sorting = models.CharField(_('Sorting'), default='', blank=True, max_length=100)
    limit = models.PositiveIntegerField(_('Limit'), default=6)
    template_name = models.CharField(_('Template name'), default='', blank=True, max_length=100)
    data = JSONField(
        _('Data'), default=dict, blank=True,
        help_text=_('Optional. Some templates may support additional options for conditional rendering.'),
    )
    ajax_load = models.BooleanField(_('AJAX load'), default=False)

    def __init__(self, *args, **kwargs):
        super(SimilarProductsPluginModel, self).__init__(*args, **kwargs)

    def __str__(self) -> str:
        return str(self.collection)
