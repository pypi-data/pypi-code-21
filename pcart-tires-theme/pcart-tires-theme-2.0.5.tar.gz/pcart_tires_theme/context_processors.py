from django.contrib.sites.shortcuts import get_current_site


def shop_data(request):
    from pcart_catalog.models import Collection
    site = get_current_site(request)

    collections_qs = Collection.objects.filter(site=site, published=True)
    collections = {x.slug: x.as_dict() for x in collections_qs}

    context ={
        'all_collections': collections,
    }
    return context
