from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import (
    Q, Prefetch, Count, Sum, Case,
    Min, Max, When,
    PositiveIntegerField, DecimalField, F)
from .models import (
    ProductType,
    ProductTypeProperty,
    Product,
    ProductVariant,
    ProductStatus,
    Vendor,
    PropertyValueSlug,
)
from django.core.paginator import Paginator
from .utils import (
    regroup_tags_for_filter_sets,
    get_tags_array_query_expression,
    normalize_filter_tags,
    group_tags_for_prefixes,
)
from . import settings as pcart_settings
from typing import Dict, List, Optional


def fix_final_slash(value):
    if not value.endswith('/'):
        return value + '/'
    return value


class ProductsFilterManager:
    MAX_PAGINATION_LIMIT = 50

    def __init__(
            self, collection,
            view='default',
            sort=pcart_settings.PCART_COLLECTION_DEFAULT_ORDERING,
            limit=None, trigger_obj=None):
        self.collection = collection
        self.url_filter_rules = collection.get_url_filter_rules()

        # Initial view
        self.collection_view = view
        self.template_name = self.get_view_attribute('template')
        self.exclude_filters_info = self.get_view_attribute('exclude_filters_info', False)

        if limit is not None and limit > self.MAX_PAGINATION_LIMIT:
            limit = self.MAX_PAGINATION_LIMIT
        self.paginate_by = limit or self.get_view_attribute('paginate_by')

        self.ordering_type = sort
        self.page = 1
        self.num_pages = 1

        # Initial filtering
        self.filter_tags = []
        self._filtered = False

        self.vendors = Vendor.objects.none()
        self.prices = (None, None)
        self._prices = False

        # Init product types
        self.product_types = self.get_product_types()
        self.properties_for_filters = self.get_properties_for_filters()
        self.visible_status_ids = self.get_visible_status_ids()
        self.property_value_slugs = self.get_property_value_slugs()

        self._products_kwargs_all = self._products_kwargs_without_variants = self._variants_kwargs = dict()

        self.trigger_obj = trigger_obj
        self.trigger_prefixes = self.trigger_obj.get_prefixes() if self.trigger_obj else None

    def set_page(self, page: int = 1):
        self.page = page

    def set_sort(self, sort: str = pcart_settings.PCART_COLLECTION_DEFAULT_ORDERING):
        self.ordering_type = sort

    def get_view_settings(self) -> Dict:
        return settings.PCART_COLLECTION_TEMPLATES[self.collection_view]

    def get_view_attribute(self, attribute, default=None):
        return self.get_view_settings().get(attribute, default)

    def set_filters(self, filter_tags=None, vendors=None, prices=None):
        if filter_tags is not None:
            self.filter_tags = filter_tags
        if vendors is not None:
            self.vendors = vendors
        if prices is not None:
            self.prices = prices
            if self.prices[0] or self.prices[1]:
                self._prices = True
            else:
                self._prices = False

    def set_view(self, view: str = 'default'):
        self.collection_view = view
        self.template_name = self.get_view_attribute('template')
        self.exclude_filters_info = self.get_view_attribute('exclude_filters_info', False)
        self.paginate_by = self.get_view_attribute('paginate_by')

    def get_product_types(self):
        return self.collection.get_product_types()

    def get_properties_for_filters(self):
        result = ProductTypeProperty.objects.filter(
            product_type__in=self.product_types, use_in_filters=True) \
            .order_by('tag_prefix') \
            .values_list('title', 'tag_prefix', 'for_variants') \
            .distinct('tag_prefix')
        return result

    def get_visible_status_ids(self):
        return ProductStatus.objects.filter(is_visible=True).values_list('id', flat=True)

    def get_property_value_slugs(self):
        return PropertyValueSlug.objects.values_list('value', 'slug')

    def get_products_kwargs_all(self) -> Dict:
        if self.collection.products_selection == 'manual':
            return {
                'collections': self.collection,
                'published': True,
                'status_id__in': self.visible_status_ids,
            }
        elif self.collection.products_selection == 'automatic':
            _result = {
                'published': True,
                'status_id__in': self.visible_status_ids,
            }
            if self.collection.condition_vendors.exists():
                _result.update({'vendor__in': self.collection.condition_vendors.all()})
            if self.collection.condition_product_types.exists():
                _result.update({'product_type__in': self.collection.condition_product_types.all()})
            if self.collection.condition_min_price > 0.0:
                _result.update({'price__gte': self.collection.condition_min_price})
            if self.collection.condition_max_price > 0.0:
                _result.update({'price__lte': self.collection.condition_max_price})
            if self.collection.mandatory_tags:
                _result.update({'tags__contains': self.collection.mandatory_tags})
            if self.collection.optional_tags:
                _result.update({'tags__overlap': self.collection.optional_tags})
            return _result

    def get_products_kwargs_without_variants(self):
        return dict(**self.get_products_kwargs_all(), **{'variants_count': 0})

    def get_variants_kwargs(self):
        return {
            'product__collections': self.collection,
            'product__published': True,
            'status_id__in': self.visible_status_ids,
        }

    def get_products(self):
        tag_groups = regroup_tags_for_filter_sets(self.filter_tags)
        tags_expr = get_tags_array_query_expression(tag_groups, 'tags')
        v_tags_expr = tags_expr
        variants__tags_expr = get_tags_array_query_expression(tag_groups, 'variants__tags')

        self._products_kwargs_all = self.get_products_kwargs_all()
        self._products_kwargs_without_variants = self.get_products_kwargs_without_variants()
        self._variants_kwargs = self.get_variants_kwargs()

        products = Product.objects.filter(**self._products_kwargs_all)
        total_max_price = products.aggregate(Max('max_variant_price'))['max_variant_price__max']

        self._filtered = False
        tag_expr_without_prices = tags_expr
        v_tag_expr_without_prices = v_tags_expr

        # Filter by price
        if self._prices:
            if self.prices[0] and self.prices[1]:
                p_price_expr_ex = \
                    Q(variants_count=0) & (Q(price__lt=self.prices[0]) | Q(price__gt=self.prices[1]))
                v_price_expr = Q(price__gte=self.prices[0]) & Q(price__lte=self.prices[1])
                variants_price_expr = Q(variants__price__gte=self.prices[0]) & Q(variants__price__lte=self.prices[1])
            elif self.prices[0] and self.prices[1] is None:
                p_price_expr_ex = Q(variants_count=0) & Q(price__lt=self.prices[0])
                v_price_expr = Q(price__gte=self.prices[0])
                variants_price_expr = Q(variants__price__gte=self.prices[0])
            elif self.prices[0] is None and self.prices[1]:
                p_price_expr_ex = Q(variants_count=0) & Q(price__gt=self.prices[1])
                v_price_expr = Q(price__lte=self.prices[1])
                variants_price_expr = Q(variants__price__lte=self.prices[1])

            self._filtered = True
            tags_expr = tags_expr & ~p_price_expr_ex
            v_tags_expr = v_tags_expr & v_price_expr
            variants__tags_expr = variants__tags_expr & variants_price_expr

        # Filter by Vendor
        if self.vendors:
            self._filtered = True
            products = products.filter(vendor__in=self.vendors)

        if self.filter_tags:
            self._filtered = True

        # Prefetch variants
        if self._filtered:
            products = products.filter(tags_expr)
            prefetch = Prefetch(
                'variants', queryset=ProductVariant.objects.filter(v_tags_expr))
        else:
            prefetch = Prefetch('variants')

        # Prefetch additional data
        products = products.prefetch_related(prefetch).prefetch_related('variants__status')
        products = products.prefetch_related('translations')
        products = products.prefetch_related('status')
        products = products.prefetch_related('status__translations')
        products = products.prefetch_related('images')
        products = products.prefetch_related('images__translations')
        products = products.prefetch_related('collections')
        products = products.prefetch_related('collections__translations')
        products = products.prefetch_related('product_type')
        products = products.prefetch_related('product_type__translations')

        # Add count, min and max annotations
        if self._filtered:
            products = products.annotate(
                filtered_variants_count=Sum(Case(
                    When(variants__tags_expr, then=1),
                    default=0,
                    output_field=PositiveIntegerField(),
                )),
                filtered_min_variant_price=Min(Case(
                    When(variants__tags_expr, then=F('variants__price')),
                    default=F('max_variant_price'),
                    output_field=DecimalField(),
                )),
                filtered_max_variant_price=Max(Case(
                    When(variants__tags_expr, then=F('variants__price')),
                    default=F('min_variant_price'),
                    output_field=DecimalField(),
                )),
            )
            products = products.exclude(Q(filtered_variants_count=0) & Q(variants_count__gt=0))

        if not self.exclude_filters_info:
            all_tags, vendor_tags = self.calculate_counters(tags_expr, v_tags_expr)
        else:
            all_tags = vendor_tags = list()

        ordering = self.get_ordering()
        products = products.order_by(*ordering)

        price_data = self.aggregate_price_data(
            products, total_max_price, tag_expr_without_prices, v_tag_expr_without_prices)

        return products, price_data, all_tags, vendor_tags

    def get_ordering(self):
        return pcart_settings.PCART_COLLECTION_ORDERINGS[
            self.ordering_type]['with_filters' if self._filtered else 'without_filters']

    def calculate_counters(self, tags_expr, v_tags_expr):
        import itertools
        from collections import Counter

        nonfiltered_vendor_counters = {
            x['vendor__slug']: x['id__count']
            for x in Product.objects.filter(
                **self._products_kwargs_without_variants).values('vendor__slug').annotate(Count('id')).order_by()}
        nonfiltered_v_vendor_counters = {
            x['product__vendor__slug']: x['id__count']
            for x in ProductVariant.objects.filter(
                **self._variants_kwargs).values('product__vendor__slug').annotate(Count('id')).order_by()}
        filtered_vendor_counters = {
            x['vendor__slug']: x['id__count']
            for x in Product.objects.filter(
                tags_expr,
                **self._products_kwargs_without_variants).values('vendor__slug').annotate(Count('id')).order_by()}
        filtered_v_vendor_counters = {
            x['product__vendor__slug']: x['id__count']
            for x in ProductVariant.objects.filter(
                v_tags_expr,
                **self._variants_kwargs).values('product__vendor__slug').annotate(Count('id')).order_by()}

        vendor_counter = Counter(filtered_vendor_counters)
        del vendor_counter[None]
        v_vendor_counter = Counter(filtered_v_vendor_counters)
        del v_vendor_counter[None]
        t_vendor_counter = vendor_counter + v_vendor_counter

        nonfiltered_vendor_counter = Counter(nonfiltered_vendor_counters)
        del nonfiltered_vendor_counter[None]
        nonfiltered_v_vendor_counter = Counter(nonfiltered_v_vendor_counters)
        del nonfiltered_v_vendor_counter[None]
        nonfiltered_t_vendor_counter = nonfiltered_vendor_counter + nonfiltered_v_vendor_counter

        _vendors_slugs = [v.slug for v in self.vendors]
        _vendors_titles = {
            slug: title for slug, title in Vendor.objects.values_list('slug', 'translations__title').distinct('slug')}

        vendor_tags = sorted([{
            'tag': t,
            'label': _vendors_titles.get(t),
            'count': nonfiltered_t_vendor_counter[t],
            'filtered': t_vendor_counter[t],
            'selected': t in _vendors_slugs,
            'active_filter': len(_vendors_slugs) > 0,
            'url': '' if t_vendor_counter[t] == 0 else fix_final_slash(self.collection.get_absolute_url() + '/'.join(
                normalize_filter_tags(
                    self.collection,
                    (
                        list(self.vendors) + [t] if t is not None else []
                    ) if t not in _vendors_slugs else [v.slug for v in self.vendors if v.slug != t],
                    self.prices,
                    self.filter_tags,
                    self.property_value_slugs,
                    self.url_filter_rules,
                    trigger=self.trigger_obj.trigger if self.trigger_obj is not None else None,
                ))),
        } for t in nonfiltered_t_vendor_counter], key=lambda x: x['label'])

        all_tags = []

        ft_groups = group_tags_for_prefixes(self.filter_tags)
        filter_prefixes = set([i.split(':')[0] for i in self.filter_tags])

        _nonfiltered_tagset = list(
            Product.objects.filter(
                **self._products_kwargs_without_variants).values_list('tags', flat=True))

        _nonfiltered_v_tagset = list(
            ProductVariant.objects.filter(**self._variants_kwargs).values_list('tags', flat=True))

        for f in self.properties_for_filters:
            tags_chunk = [k for k in self.filter_tags if k.split(':')[0] != f[1]]
            _prefix = f[1]

            tag_groups = regroup_tags_for_filter_sets(tags_chunk)
            tags_expr = get_tags_array_query_expression(tag_groups, 'tags')

            _args = [tags_expr]
            _kwargs = dict(self._products_kwargs_without_variants)
            if self.vendors:
                _kwargs.update({'vendor__in': self.vendors})

            tagset = list(Product.objects.filter(*_args, **_kwargs).values_list('tags', flat=True))
            tagset = [x for x in itertools.chain(*[t for t in tagset]) if x.startswith(_prefix+':')]
            nonfiltered_tagset = [
                x for x in itertools.chain(*[t for t in _nonfiltered_tagset]) if x.startswith(_prefix + ':')]

            _args = [tags_expr]
            _kwargs = dict(self._variants_kwargs)
            if self.vendors:
                _kwargs.update({'product__vendor__in': self.vendors})

            v_tagset = list(ProductVariant.objects.filter(*_args, **_kwargs).values_list('tags', flat=True))
            v_tagset = [x for x in itertools.chain(*[t for t in v_tagset]) if x.startswith(_prefix+':')]
            nonfiltered_v_tagset = [
                x for x in itertools.chain(*[t for t in _nonfiltered_v_tagset]) if x.startswith(_prefix + ':')]

            counter = Counter(tagset)
            v_counter = Counter(v_tagset)
            t_counter = counter + v_counter

            nonfiltered_counter = Counter(nonfiltered_tagset)
            nonfiltered_v_counter = Counter(nonfiltered_v_tagset)
            nonfiltered_t_counter = nonfiltered_counter + nonfiltered_v_counter

            all_tags.append({
                'group_label': f[0],
                'prefix': _prefix,
                'tags': sorted([
                {
                    'tag': t,
                    'label': t.split(':')[-1],
                    'prefix': _prefix,
                    'selected': t in self.filter_tags,
                    'active_filter': _prefix in filter_prefixes,
                    'count': nonfiltered_t_counter[t],
                    'url': '' if t_counter[t] == 0 else fix_final_slash(self.collection.get_absolute_url() + '/'.join(
                        normalize_filter_tags(
                            self.collection,
                            self.vendors,
                            self.prices,
                            (
                                self.filter_tags+[t]
                            ) if t not in self.filter_tags else [x for x in self.filter_tags if x != t],
                            self.property_value_slugs,
                            self.url_filter_rules,
                            trigger=self.trigger_obj.trigger
                            if self.trigger_obj is not None and _prefix not in self.trigger_obj.get_prefixes()
                            else None,
                        ))),
                    'filtered': t_counter[t],
                } for t in nonfiltered_t_counter], key=self.tags_sort_func)})

        return all_tags, vendor_tags

    @staticmethod
    def tags_sort_func(x):
        import re

        def atoi(text):
            return int(text) if text.isdigit() else text

        def natural_keys(text):
            '''
            alist.sort(key=natural_keys) sorts in human order
            http://nedbatchelder.com/blog/200712/human_sorting.html
            (See Toothy's implementation in the comments)
            '''
            return [atoi(c) for c in re.split(r'(\d+)', text)]


        value = x['label'].strip()
        t = value.replace(',', '.').replace('/', '.').replace(' ', '')
        value = natural_keys(t)
        return value

    def aggregate_price_data(self, products, total_max_price, tag_expr_without_prices, v_tag_expr_without_prices):
        if self._filtered:
            p_agg_data = products.filter(variants_count=0).aggregate(Max('price'), Min('price'))
            v_agg_data = products.filter(variants_count__gt=0).aggregate(
                Min('filtered_min_variant_price'),
                Max('filtered_max_variant_price'),
                Sum('filtered_variants_count'),
            )
            variants_count = v_agg_data['filtered_variants_count__sum']
            min_price = min(
                [x for x in [p_agg_data['price__min'], v_agg_data['filtered_min_variant_price__min']] if
                 x is not None] or [0])
            max_price = max(
                [x for x in [p_agg_data['price__max'], v_agg_data['filtered_max_variant_price__max']] if
                 x is not None] or [total_max_price])

            pa_query = Product.objects.filter(tag_expr_without_prices, **self._products_kwargs_without_variants)
            va_query = ProductVariant.objects.filter(
                v_tag_expr_without_prices,
                **self._variants_kwargs)
            if self.vendors:
                pa_query = pa_query.filter(vendor__in=self.vendors)
                va_query = va_query.filter(product__vendor__in=self.vendors)
            pa_agg_data = pa_query.aggregate(Max('price'), Min('price'))
            va_agg_data = va_query.aggregate(Max('price'), Min('price'))

            min_available_price = min(
                [x for x in [pa_agg_data['price__min'], va_agg_data['price__min']] if x is not None] or [0])
            max_available_price = max(
                [x for x in [pa_agg_data['price__max'], va_agg_data['price__max']] if x is not None] or [
                    total_max_price])
        else:
            p_agg_data = products.filter(variants_count=0).aggregate(Max('price'), Min('price'))
            v_agg_data = products.filter(variants_count__gt=0).aggregate(
                Min('min_variant_price'),
                Max('max_variant_price'),
                Sum('variants_count'),
            )
            variants_count = v_agg_data['variants_count__sum']
            min_price = min(
                [x for x in [p_agg_data['price__min'], v_agg_data['min_variant_price__min']] if x is not None] or [0])
            max_price = max(
                [x for x in [p_agg_data['price__max'], v_agg_data['max_variant_price__max']] if x is not None] or [
                    total_max_price])

            pa_query = Product.objects.filter(**self._products_kwargs_without_variants)
            va_query = ProductVariant.objects.filter(**self._variants_kwargs)
            pa_agg_data = pa_query.aggregate(Max('price'), Min('price'))
            va_agg_data = va_query.aggregate(Max('price'), Min('price'))

            min_available_price = min(
                [x for x in [pa_agg_data['price__min'], va_agg_data['price__min']] if x is not None] or [0])
            max_available_price = max(
                [x for x in [pa_agg_data['price__max'], va_agg_data['price__max']] if x is not None] or [
                    total_max_price])

        data = {
            'variants_count': variants_count,
            'prices': self.prices,
            'min_available_price': min_available_price,
            'max_available_price': max_available_price,
            'min_price': min_price,
            'max_price': max_price,
            'min_selected_price': self.prices[0] or min_price,
            'max_selected_price': self.prices[1] or max_price,
        }
        return data

    def paginate_products(self, products):
        _products_list = products
        if self.paginate_by is None and _products_list.count() > self.MAX_PAGINATION_LIMIT:
            self.paginate_by = self.MAX_PAGINATION_LIMIT

        if self.paginate_by is not None:
            paginator = Paginator(_products_list, self.paginate_by)
            self.num_pages = paginator.num_pages
            products = paginator.page(self.page)
        return products

    def get_context(self):
        products, price_data, all_tags, vendor_tags = self.get_products()
        context = {
            'collection': self.collection,
            'products': self.paginate_products(products),
            'filter_tags': self.filter_tags,
            'all_tags': all_tags,
            'vendor_tags': vendor_tags,
            'ordering_type': self.ordering_type,
            'filtered': self._filtered,
            'page_number': self.page,
            'collection_view': self.collection_view,
            'template_name': self.template_name,
        }
        context.update(price_data)
        return context

    def render_to_string(self, request=None):
        return render_to_string(self.template_name, context=self.get_context(), request=request)
