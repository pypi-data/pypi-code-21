from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_delete
from django.dispatch import receiver
import uuid


class XLSImportProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_('Title'), max_length=255, unique=True)
    language = models.CharField(_('Language'), max_length=10)

    first_row_as_labels = models.BooleanField(
        _('First row as labels'), default=True,
        help_text=_('Get column labels from the first row.')
    )

    default_product_type = models.ForeignKey(
        'pcart_catalog.ProductType', verbose_name=_('Default product type'))
    default_collection = models.ForeignKey(
        'pcart_catalog.Collection', verbose_name=_('Default collection'))

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('XLS Import profile')
        verbose_name_plural = _('XLS Import profiles')
        ordering = ['title']

    def __str__(self):
        return self.title


class XLSColumn(models.Model):
    DESTINATION_CHOICES = (
        ('product_type', _('Product type')),
        ('collection', _('Collection')),
        ('extra_collection', _('Extra collection')),
        ('vendor', _('Vendor')),
        ('product', _('Product')),
        ('id', _('ID')),
        ('external_id', _('External ID')),
        ('product_image', _('Product image')),
        ('product_property', _('Product property')),
        ('price', _('Price')),
        ('quantity', _('Quantity')),
        ('product_status', _('Status')),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        XLSImportProfile, verbose_name=_('Import profile'),
        related_name='columns',
    )
    column_index = models.CharField(_('Column index'), max_length=100, blank=True, default='')
    use_column_label = models.BooleanField(
        _('Use column label'), default=True,
        help_text=_('If checked "Column index" is related to column label, otherwise it is a column number.')
    )
    destination = models.CharField(
        _('Destination'), max_length=100, choices=DESTINATION_CHOICES,
        help_text=_('See documentation for supported values.')
    )
    sub_destination = models.CharField(_('Sub-destination'), max_length=100, default='', blank=True)

    function = models.TextField(
        _('Function'), default='', blank=True,
        help_text=_('Use P-Cart Script for implementing complex logic.')
    )

    class Meta:
        verbose_name = _('XLS column')
        verbose_name_plural = _('XLS columns')
        ordering = ['column_index']

    def __str__(self):
        return self.column_index

    def get_destination(self):
        if self.sub_destination:
            return '%s:%s' % (self.destination, self.sub_destination)
        else:
            return self.destination

def generate_price_list_filename(instance, filename):
    """
    Returns a price list file name.
    """
    ext = filename.split('.')[-1]
    url = 'import/xls-price-lists/%s/%s.%s' % (
        instance.id, str(instance.id).replace('-', ''), ext)
    return url


class XLSPriceList(models.Model):
    XLS_PRICE_LIST_STATUS_CHOICES = (
        ('new', _('New')),
        ('processing', _('Processing')),
        ('success', _('Success')),
        ('with_errors', _('With errors')),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        XLSImportProfile, verbose_name=_('Import profile'),
        related_name='price_lists',
    )
    file = models.FileField(
        _('Price list'), upload_to=generate_price_list_filename,
        help_text=_('Price list file.'),
    )

    status = models.CharField(
        _('Status'), default='new', max_length=70, choices=XLS_PRICE_LIST_STATUS_CHOICES)

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('XLS Price list')
        verbose_name_plural = _('XLS Price lists')
        ordering = ['added']

    def __str__(self):
        return str(self.file)

    @staticmethod
    def cell_to_str(cell):
        """Returns a cell value as string."""
        if cell.ctype == 1:  # string
            return str(cell.value).strip()
        elif cell.ctype == 2:  # number
            if cell.value == int(cell.value):
                return str(int(cell.value))
            else:
                return str(float(cell.value))
        else:
            return str(cell.value)

    def load_data(self, limit=50):
        import xlrd
        from pcart_script.interpreter import LispInterpreter
        workbook = xlrd.open_workbook(self.file.path)
        sheet = workbook.sheet_by_index(0)

        labels = None
        start_row = 0
        if self.profile.first_row_as_labels:
            labels = [self.cell_to_str(x) for x in sheet.row(0)]
            start_row = 1
        stop_row = sheet.nrows

        columns = self.profile.columns.all()

        result = []
        for i in range(start_row, stop_row):
            if limit is not None and i > limit:
                break

            row = [self.cell_to_str(x) for x in sheet.row(i)]
            chunk = []

            for col in columns:
                if col.column_index == '':
                    index = None
                elif self.profile.first_row_as_labels and col.use_column_label:
                    index = labels.index(col.column_index)
                else:
                    index = int(col.column_index)

                if col.function:
                    _value = row[index] if index is not None else ''
                    if labels:
                        _columns = {k: v for k, v in zip(labels, row)}
                    else:
                        _columns = {k: v for k, v in zip(range(len(row)), row)}
                    _result = LispInterpreter(
                        code=col.function,
                        globals={
                            'value': _value,
                            'columns': _columns,
                        },
                    ).execute()
                    if _result is None:
                        # Ignore line if function returned #nil
                        chunk = []
                        break
                    chunk.append(_result)
                else:
                    chunk.append(row[index] if index is not None else '')

            if chunk:
                result.append(chunk)

        meta = {
            'labels': labels,
            'columns': columns,
        }

        return result, meta

    def process(self):
        from decimal import Decimal
        from urllib.error import URLError
        from pcart_catalog.models import (
            Vendor,
            Product,
            ProductImage,
            ProductStatus,
            ProductType,
            Collection,
        )
        from pcart_core.utils import get_unique_slug

        self.status = 'processing'
        self.save()

        status_available = ProductStatus.objects.order_by('-weight').first()
        status_unavailable = ProductStatus.objects.order_by('-weight').last()

        try:
            result, meta = self.load_data(limit=None)

            columns = meta['columns']

            for item in result:
                chunk = {k.get_destination(): v for k, v in zip(columns, item)}

                try:
                    if 'id' in chunk:
                        product = Product.objects.get(pk=chunk['id'])
                    elif 'external_id' in chunk:
                        product = Product.objects.get(external_id=chunk['external_id'])
                    else:
                        product = Product()
                        if 'id' in chunk:
                            product.id = chunk['id']
                        if 'external_id' in chunk:
                            product.external_id = chunk['external_id']
                except Product.DoesNotExist:
                    product = Product()
                    if 'id' in chunk:
                        product.id = chunk['id']
                    if 'external_id' in chunk:
                        product.external_id = chunk['external_id']

                product.set_current_language(self.profile.language)
                product.product_type = self.profile.default_product_type
                if 'product_type' in chunk:
                    try:
                        p_type = ProductType.objects.translated(
                            self.profile.language,
                            title=chunk['product_type']).get()
                        product.product_type = p_type
                    except ProductType.DoesNotExist:
                        XLSImportHistory.objects.create(
                            price_list=self, success=False,
                            message='Ignore row\n%s\nProduct type "%s" not found.' % (chunk, chunk['product_type']),
                        )
                        continue

                product.title = chunk.get('product:title')
                if not product.title:
                    XLSImportHistory.objects.create(
                        price_list=self, success=False,
                        message='Ignore row\n%s\nProduct title is empty.' % chunk,
                    )
                    continue

                if 'vendor' in chunk:
                    try:
                        vendor = Vendor.objects.translated(
                            self.profile.language,
                            title=chunk['vendor']).get()
                    except Vendor.DoesNotExist:
                        vendor = Vendor()
                        vendor.set_current_language(self.profile.language)
                        vendor.title=chunk['vendor']
                        vendor.slug=get_unique_slug(chunk['vendor'], Vendor)
                        vendor.save()
                    product.vendor = vendor

                if not product.slug:
                    product.slug = get_unique_slug(product.title, Product)
                product.description = chunk.get('product:description', '')
                product.sku = chunk.get('product:sku', '')
                product.barcode = chunk.get('product:barcode', '')
                product.weight = float(chunk.get('product:weight', 0.0))

                _props = {}
                for c in chunk.keys():
                    if c.startswith('product_property:'):
                        _props[c[17:]] = chunk[c]
                product.properties = _props

                # TODO: fix it
                if 'quantity' in chunk:
                    _quantity = int(chunk['quantity'])
                    product.quantity = _quantity
                    if _quantity > 0:
                        product.status = status_available
                    else:
                        product.status = status_unavailable
                else:
                    product.status = status_available

                product.price = Decimal(chunk.get('price', '0.0'))
                product.save()

                if 'collection' in chunk:
                    try:
                        collection = Collection.objects.translated(
                            self.profile.language,
                            title=chunk['collection']).get()
                        product.collections = [collection]
                    except Collection.DoesNotExist:
                        XLSImportHistory.objects.create(
                            price_list=self, success=False,
                            message='Ignore row\n%s\nCollection "%s" not found.' % (chunk, chunk['collection']),
                        )
                        continue
                else:
                    product.collections = [self.profile.default_collection]

                images_links = []
                im_keys = []
                for im in chunk:
                    if im.startswith('product_image:'):
                        im_keys.append(im.split(':'))
                im_keys = sorted(im_keys, key=lambda x: int(x[1]))
                # print(im_keys)
                for k in im_keys:
                    # print(k)
                    images_links.append(chunk['{}:{}'.format(*k)])

                images_for_delete = product.images.exclude(download_link__in=images_links)
                if images_for_delete:
                    images_for_delete.delete()

                available_images_links = list(product.images.values_list('download_link', flat=True))
                for im in images_links:
                    if im and im not in available_images_links:
                        # print(im)
                        try:
                            image = ProductImage(
                                product=product,
                                download_link=im,
                            )
                            image.set_current_language(self.profile.language)
                            image.save()
                        except URLError:
                            XLSImportHistory.objects.create(
                                price_list=self, success=False, product=product,
                                message='Image download error\n%s\nCannot download image "%s".' % (chunk, im),
                            )
                        except Exception as e:
                            XLSImportHistory.objects.create(
                                price_list=self, success=False, product=product,
                                message='Image download error\n%s\n%s' % (chunk, e),
                            )

                product.save()
                XLSImportHistory.objects.create(
                    price_list=self, success=True, product=product,
                    message='Image download error\n%s' % chunk,
                )

            self.status = 'success'
            self.save()
        except Exception as e:
            self.status = 'failed'
            self.save()
            raise e


@receiver(post_delete, sender=XLSPriceList)
def price_list_post_delete_listener(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete(save=False)


class XLSImportHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    price_list = models.ForeignKey(XLSPriceList, verbose_name=_('Price list'), related_name='history')
    product = models.ForeignKey(
        'pcart_catalog.Product', verbose_name=_('Product'),
        related_name='xls_import_history', null=True, blank=True)

    success = models.BooleanField(_('Success'), default=True)
    message = models.TextField(_('Message'), default='', blank=True)

    added = models.DateTimeField(_('Added'), auto_now_add=True)

    class Meta:
        verbose_name = _('XLS Import history')
        verbose_name_plural = _('XLS Import history')
        ordering = ['added']

    def __str__(self):
        return '%s - %s' % (self.price_list, self.product)
