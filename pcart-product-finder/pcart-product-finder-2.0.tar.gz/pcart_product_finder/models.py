from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import ArrayField
from parler.models import TranslatableModel, TranslatedFields
# from parler.managers import TranslatableManager, TranslatableQuerySet
from cms.models import CMSPlugin
from adminsortable.models import SortableMixin
from pcart_catalog.models import MAX_TAG_LENGTH
import uuid


class FilterName(TranslatableModel, SortableMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    translations = TranslatedFields(
        title=models.CharField(_('Title'), max_length=255, unique=True),
    )
    default = models.BooleanField(_('Default'), default=False)
    position = models.PositiveIntegerField(_('Position'), default=0, editable=False, db_index=True)

    class Meta:
        verbose_name = _('Filter name')
        verbose_name_plural = _('Filter names')
        ordering = ['position']

    def __str__(self) -> str:
        return self.title


def generate_object_vendor_image_filename(instance: 'ObjectVendor', filename: str) -> str:
    ext = filename.split('.')[-1]
    url = 'images/object-vendors/%s/%s.%s' % (instance.id, str(uuid.uuid4()).replace('-', ''), ext)
    return url


class ObjectVendor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_('Title'), max_length=255, unique=True)
    image = models.ImageField(_('Image'), null=True, blank=True, upload_to=generate_object_vendor_image_filename)

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Object vendor')
        verbose_name_plural = _('Object vendors')
        ordering = ['title']

    def __str__(self) -> str:
        return self.title


def generate_object_model_image_filename(instance: 'ObjectVendor', filename: str) -> str:
    ext = filename.split('.')[-1]
    url = 'images/object-models/%s/%s.%s' % (instance.id, str(uuid.uuid4()).replace('-', ''), ext)
    return url


class ObjectModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    object_vendor = models.ForeignKey(
        ObjectVendor, verbose_name=_('Object vendor'),
        related_name='models',
        on_delete=models.CASCADE)
    title = models.CharField(_('Title'), max_length=255)
    image = models.ImageField(_('Image'), null=True, blank=True, upload_to=generate_object_model_image_filename)

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Object model')
        verbose_name_plural = _('Object models')

    def __str__(self) -> str:
        return self.title


class ObjectGeneration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    object_model = models.ForeignKey(
        ObjectModel, verbose_name=_('Object model'),
        related_name='generations',
        on_delete=models.CASCADE)
    start_production = models.PositiveIntegerField(_('Start production'))
    finish_production = models.PositiveIntegerField(_('Finish production'), null=True, blank=True)
    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Object generation')
        verbose_name_plural = _('Object generations')
        unique_together = ['object_model', 'start_production', 'finish_production']

    def __str__(self):
        return '%s-%s' % (self.start_production, self.finish_production)


class ObjectVariant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    object_generation = models.ForeignKey(
        ObjectGeneration, verbose_name=_('Object generation'),
        related_name='variants',
        on_delete=models.CASCADE)
    title = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=255)
    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Object variant')
        verbose_name_plural = _('Object variants')
        unique_together = ['object_generation', 'slug']

    def __str__(self) -> str:
        return '%s %s %s (%s)' % (
            str(self.object_generation.object_model.object_vendor),
            str(self.object_generation.object_model),
            self.title,
            str(self.object_generation),
        )

    def get_grouped_filters(self, collection=None):
        from collections import OrderedDict
        from pcart_catalog.utils import normalize_filter_tags

        filter_names = FilterName.objects.order_by('-default')
        result = OrderedDict()
        for f in filter_names:
            result[f.title] = []
        filters = self.filters.all()
        if collection:
            filters = filters.filter(collection_slug=collection.slug)
        for f in filters:
            item = {
                'title': f.title,
                'tags': f.tags,
            }
            if collection:
                url = collection.get_absolute_url() + '/'.join(
                    normalize_filter_tags(
                        collection,
                        tags=f.tags,
                        trigger=self.slug,
                    ))
                if not url.endswith('/'):
                    url += '/'
                item['url'] = url
                item['count'] = collection.products.filter(
                    published=True, status__is_visible=True, tags__contains=f.tags).count()
            result[f.filter_name.title].append(item)
        return result


class ObjectFilter(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    object_variant = models.ForeignKey(
        ObjectVariant, verbose_name=_('Object variant'),
        related_name='filters',
        on_delete=models.CASCADE)
    title = models.CharField(_('Title'), max_length=255)
    filter_name = models.ForeignKey(
        FilterName, verbose_name=_('Filter name'),
        related_name='filters',
        on_delete=models.CASCADE)
    collection_slug = models.CharField(_('Collection slug'), max_length=150)
    tags = ArrayField(
        models.CharField(max_length=MAX_TAG_LENGTH), verbose_name=_('Tags'),
        default=list, blank=True,
    )

    class Meta:
        verbose_name = _('Object filter')
        verbose_name_plural = _('Object filters')
        unique_together = ['object_variant', 'title', 'filter_name']
        ordering = ['title']

    def __str__(self) -> str:
        return self.title


class ProductFinderConfig(TranslatableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    translations = TranslatedFields(
        vendor_title=models.CharField(_('Vendor title'), max_length=150),
        model_title=models.CharField(_('Model title'), max_length=150),
        generation_title=models.CharField(_('Generation title'), max_length=150),
        variant_title=models.CharField(_('Variant title'), max_length=150),
    )

    class Meta:
        verbose_name = _('Product finder config')
        verbose_name_plural = _('Product finder config')

    def __str__(self) -> str:
        return str(self.pk)


# CMS plugins


class ProductFinderFormPluginModel(CMSPlugin):
    """
    Represents a product finder form.
    """
    title = models.CharField(_('Title'), max_length=255, default='', blank=True)
    collection = models.ForeignKey(
        'pcart_catalog.Collection', verbose_name=_('Collection'), on_delete=models.CASCADE,
    )

    def __init__(self, *args, **kwargs):
        super(ProductFinderFormPluginModel, self).__init__(*args, **kwargs)

    def __str__(self) -> str:
        if self.title:
            return '%s - %s' % (self.title, self.collection)
        else:
            return str(self.collection)
