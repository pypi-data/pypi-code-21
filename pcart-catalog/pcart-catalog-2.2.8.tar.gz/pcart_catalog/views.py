import re
# from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.http import Http404, QueryDict, HttpResponseNotFound, JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect, render
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.conf import settings
from django.utils.module_loading import import_string
from . import settings as pcart_settings
from .models import (
    Collection,
    Product,
    ProductVariant,
)
from .utils import (
    split_collection_slug,
    filter_slug_to_tags,
    normalize_filter_tags,
)


AVAILABLE_COLLECTION_PARAMS = [
    'page', 'sort', 'view', 'json', 'limit', 'ignore-tags-check', 'data']
COLLECTION_CACHE_TIMEOUT = 60 * 15


@require_http_methods(['GET'])
def collection_view(request, slug, view='default'):
    """
    Returns a filtered or non-filtered collection page.
    """
    from django.core.paginator import PageNotAnInteger, EmptyPage
    from .filtering import ProductsFilterManager

    # Ignore caching for staff users
    use_cache = request.user.is_anonymous or request.user.is_staff is False

    # Check AJAX
    is_ajax = request.is_ajax()

    # Check the GET parameters and filter only allowed
    _params = QueryDict(mutable=True)
    for k, v in request.GET.items():
        if k in AVAILABLE_COLLECTION_PARAMS:
            _params.update({k: v})

    # Check some additional arguments
    # Specify `json=true` if you need return JSON instead HTML as a response
    json_response = request.GET.get('json', False) == 'true'
    ignore_tags_check = request.GET.get('ignore-tags-check', False) == 'true'
    # Type of ordering if it is not default one
    ordering_type = request.GET.get('sort', pcart_settings.PCART_COLLECTION_DEFAULT_ORDERING)
    # Collection template is it is not default one
    collection_view = request.GET.get('view', view)
    # Extra data for context
    context_data = request.GET.get('data', '')

    collection_view_config = getattr(settings, 'PCART_COLLECTION_TEMPLATES', {}).get(collection_view)
    if collection_view_config is None:
        # Unknown view
        raise Http404
    else:
        if collection_view_config.get('ajax_only', False) and not is_ajax:
            # Ajax only view cannot be accessible via regular request
            return HttpResponseForbidden('Invalid request.')

    # Number of products on a single page
    limit = request.GET.get('limit')
    if limit is not None:
        try:
            limit = int(limit)
        except ValueError:
            limit = None

    page = request.GET.get('page')
    if page is None:
        page = '1'
    elif page == '1':
        # Remove `page` attribute if `page=1` and do redirect
        redirect_url = request.path
        if _params:
            del _params['page']
            if _params:
                redirect_url += '?%s' % _params.urlencode()
        response = redirect(redirect_url)
        return response

    # Build a cache key string
    cache_key = '%s?%s%s' % (
        request.path_info,
        _params.urlencode(),
        '|ajax' if is_ajax else '')

    if use_cache:
        result = cache.get(cache_key)
        if result and not json_response:
            return result

    collection_slug, filter_chunks = split_collection_slug(slug)
    try:
        collection = Collection.objects.get(slug=collection_slug, site_id=get_current_site(request).id)
    except Collection.DoesNotExist:
        response = HttpResponseNotFound('collection not found')
        if use_cache:
            cache.set(cache_key, response, COLLECTION_CACHE_TIMEOUT)
        return response

    # Work with optional trigger
    trigger = None
    trigger_cls = None
    trigger_obj = None
    _no_trigger_redirect = False
    if collection.trigger_module and collection.trigger_regex:
        if filter_chunks:
            m = re.fullmatch(collection.trigger_regex, filter_chunks[0])
            if m:
                trigger = filter_chunks[0]
                filter_chunks = filter_chunks[1:]
                trigger_cls = import_string(collection.trigger_module)
                trigger_obj = trigger_cls(collection, trigger)
                # If trigger is not allowed then force a redirect
                if not trigger_obj.exists():
                    trigger = None
                    _no_trigger_redirect = True

    # Split the url to tags and meta info
    filter_tags, vendors, prices, normalized_url_chunks, _redirect = \
        filter_slug_to_tags(collection, filter_chunks, trigger=trigger)

    if trigger:
        if filter_tags:
            _check_tags = trigger_obj.check_tags(filter_tags)
            # print('_check_tags =', _check_tags)
            if not _check_tags:
                del normalized_url_chunks[0]    # Remove trigger from the chunks list
                trigger = None
                _no_trigger_redirect = True
        else:
            _default_tags = trigger_obj.get_default_tags()
            # print('_default_tags =', _default_tags)
            redirect_url = collection.get_absolute_url() + '/'.join(
                normalize_filter_tags(
                    collection,
                    vendors,
                    prices,
                    _default_tags,
                    trigger=trigger,
                ))
            if not redirect_url.endswith('/'):
                redirect_url += '/'
            if _params:
                redirect_url += '?%s' % _params.urlencode()
            response = redirect(redirect_url)
            if use_cache:
                cache.set(cache_key, response, COLLECTION_CACHE_TIMEOUT)
            return response

    # Make a redirect if filter tags are in incorrect order or trigger is unavailable
    if _redirect or _no_trigger_redirect:
        redirect_url = collection.get_absolute_url() + '/'.join(normalized_url_chunks)
        if not redirect_url.endswith('/'):
            redirect_url += '/'
        if _params:
            redirect_url += '?%s' % _params.urlencode()
        response = redirect(redirect_url)
        if use_cache:
            cache.set(cache_key, response, COLLECTION_CACHE_TIMEOUT)
        return response

    # Filter products
    filter_manager = ProductsFilterManager(
        collection=collection, view=collection_view, sort=ordering_type, limit=limit,
        trigger_obj=trigger_obj,
    )
    filter_manager.set_page(page)
    filter_manager.set_filters(filter_tags=filter_tags, vendors=vendors, prices=prices)

    # Get a full information about filtered products
    try:
        context = filter_manager.get_context()
    except PageNotAnInteger:
        redirect_url = request.path
        if _params:
            del _params['page']
            redirect_url += '?%s' % _params.urlencode()
        response = redirect(redirect_url)
        if use_cache:
            cache.set(cache_key, response, COLLECTION_CACHE_TIMEOUT)
        return response
    except EmptyPage:
        redirect_url = request.path
        if _params:
            _params['page'] = str(filter_manager.num_pages)
            redirect_url += '?%s' % _params.urlencode()
        response = redirect(redirect_url)
        if use_cache:
            cache.set(cache_key, response, COLLECTION_CACHE_TIMEOUT)
        return response

    if not filter_manager.exclude_filters_info:
        # Check tags availability
        available_tags = set()
        for g in context['all_tags']:
            for t in g['tags']:
                if t['filtered'] > 0:
                    available_tags.add(t['tag'])
        _verified_filter_tags = [t for t in filter_tags if t in available_tags]

        # URL should be fixed is some filter tags are not correct, then do redirect
        if not ignore_tags_check and filter_tags != _verified_filter_tags:
            redirect_url = collection.get_absolute_url() + '/'.join(
                normalize_filter_tags(
                    collection,
                    vendors,
                    prices,
                    _verified_filter_tags,
                ))
            if not redirect_url.endswith('/'):
                redirect_url += '/'
            if _params:
                redirect_url += '?%s' % _params.urlencode()
            response = redirect(redirect_url)
            if use_cache:
                cache.set(cache_key, response, COLLECTION_CACHE_TIMEOUT)
            return response

    context.update({
        'is_ajax': is_ajax,
        'page_url': request.path,
        'trigger': trigger,
        'trigger_obj': trigger_obj,
        'ordering': ordering_type,
        'view': collection_view,
        'context_data': context_data,
    })
    if json_response:
        context['collection'] = collection.as_dict()
        context['products'] = list(map(lambda x: x.as_dict(), context['products']))
        response = JsonResponse(context, safe=True)
        return response
    else:
        response = render(request, context['template_name'], context)
        if use_cache:
            cache.set(cache_key, response, COLLECTION_CACHE_TIMEOUT)
        return response


@csrf_exempt
@require_http_methods(['POST'])
def filter_form_dispatcher(request, collection_slug):
    from .utils import get_property_slugs

    vendors = request.POST.getlist('vendor')
    filter_tags = request.POST.getlist('tag')

    price = request.POST.get('price')
    if price is not None:
        price_from, price_to = price.split(request.POST.get('price-delimiter', ','))
    else:
        price_from = request.POST.get('price-from')
        price_to = request.POST.get('price-to')

    try:
        price_from = float(price_from)
    except ValueError:
        price_from = None
    except TypeError:
        price_from = None

    try:
        price_to = float(price_to)
    except ValueError:
        price_to = None
    except TypeError:
        price_to = None

    prices = (price_from, price_to)

    collection_view = request.POST.get('view')
    ordering_type = request.POST.get('sort')
    context_data = request.POST.get('context-data')

    collection = Collection.objects.get(slug=collection_slug)
    _url = collection.get_absolute_url() + '/'.join(
        normalize_filter_tags(
            collection,
            vendors,
            prices,
            filter_tags,
            get_property_slugs(),
        ))
    if not _url.endswith('/'):
        _url += '/'

    q_attrs = QueryDict(mutable=True)
    if collection_view:
        q_attrs.update({'view': collection_view})
    if ordering_type:
        q_attrs.update({'sort': ordering_type})
    if context_data:
        q_attrs.update({'data': context_data})
    if q_attrs:
        _url += '?%s' % q_attrs.urlencode()

    return redirect(_url)


def redirect_to_collections(request):
    return redirect('pcart_collection:all-collections')


class ProductDetailView(DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'catalog/product.html'

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)

        object_id = self.get_object().id
        setattr(self.request, 'productid', object_id)

        return context

    def get_object(self, queryset=None):
        try:
            if queryset is None:
                queryset = self.model.objects.filter(published=True)
            product = queryset.get(slug=self.kwargs['product_slug'])
            setattr(self.request, 'product', product)
            return product
        except Product.DoesNotExist:
            raise Http404


class ProductVariantDetailView(DetailView):
    model = ProductVariant
    context_object_name = 'variant'
    template_name = 'catalog/variant.html'

    def get_context_data(self, **kwargs):
        context = super(ProductVariantDetailView, self).get_context_data(**kwargs)

        object = self.get_object()
        object_id = object.id

        setattr(self.request, 'productid', object_id)

        return context

    def get_object(self, queryset=None):
        try:
            if queryset is None:
                queryset = self.model.objects.filter(product__published=True)
            return queryset.get(slug=self.kwargs['variant_slug'], product__slug=self.kwargs['product_slug'])
        except Product.DoesNotExist:
            raise Http404


def collections_list_view(request, template_name='catalog/collections.html'):
    collections = Collection.objects.filter(published=True)
    context = {
        'collections': collections,
        'page_url': request.path,
    }
    return render(request, template_name, context)
