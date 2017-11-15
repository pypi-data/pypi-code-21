from celery import task
# from django.conf import settings


@task
def rename_property_name(product_type_id, old_name, new_name):
    if old_name == new_name:
        return None
    from .models import ProductType, Product, ProductVariant
    product_type = ProductType.objects.get(pk=product_type_id)
    products = Product.objects.filter(
        product_type=product_type, properties__has_key=old_name)
    product_variants = ProductVariant.objects.filter(
        product__product_type=product_type, properties__has_key=old_name)

    for p in products:
        _props = p.properties
        if old_name in _props:
            _props[new_name] = _props[old_name]
            del _props[old_name]
            p.save()

    for p in product_variants:
        _props = p.properties
        if old_name in _props:
            _props[new_name] = _props[old_name]
            del _props[old_name]
            p.save()


@task
def update_product_tags(product_type_id, property_title):
    from django.db.models import F
    from .models import ProductType, Product, ProductVariant
    product_type = ProductType.objects.get(pk=product_type_id)
    products = Product.objects.filter(
        product_type=product_type, properties__has_key=property_title)
    product_variants = ProductVariant.objects.filter(
        product__product_type=product_type, properties__has_key=property_title)

    products.update(sku=F('sku'))
    product_variants.update(sku=F('sku'))


@task
def generate_price_aggregation_file(price_aggregation_profile_id):
    from .models import PriceAggregationProfile
    profile = PriceAggregationProfile.objects.get(pk=price_aggregation_profile_id)
    profile.generate()


# Run this task automatically every 6 hours
@task.periodic_task(run_every=60*60*6)
def update_property_value_slugs():
    from .models import PropertyValueSlug
    PropertyValueSlug.objects.update_data()


@task.periodic_task(run_every=60*60*12)
def update_price_aggregation_files():
    from .models import PriceAggregationProfile
    profiles = PriceAggregationProfile.objects.all()
    for p in profiles:
        generate_price_aggregation_file.delay(p.pk)
