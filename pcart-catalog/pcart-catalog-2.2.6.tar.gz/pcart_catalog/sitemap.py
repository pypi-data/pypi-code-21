from django.contrib.sitemaps import GenericSitemap
from .models import Collection, Product, ProductVariant


COLLECTIONS_SITEMAP_CONFIG = {
    'queryset': Collection.objects.filter(published=True),
    'date_field': 'changed',
}


CollectionSitemap = GenericSitemap(COLLECTIONS_SITEMAP_CONFIG)


PRODUCT_SITEMAP_CONFIG = {
    'queryset': Product.objects.filter(published=True).prefetch_related('images'),
    'date_field': 'changed',
}


ProductSitemap = GenericSitemap(PRODUCT_SITEMAP_CONFIG, changefreq='daily')


PRODUCT_VARIANT_SITEMAP_CONFIG = {
    'queryset': ProductVariant.objects.filter(product__published=True),
    'date_field': 'changed',
}


ProductVariantSitemap = GenericSitemap(PRODUCT_VARIANT_SITEMAP_CONFIG, changefreq='daily')
