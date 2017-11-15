from pcart_catalog.triggers import BaseCollectionTrigger
from .models import ObjectVariant


class ProductFinderTrigger(BaseCollectionTrigger):
    def __init__(self, collection, trigger):
        self.collection = collection
        self.trigger = trigger
        self.tags_list = []
        self.default_tags = []
        self.prefixes_set = set()
        try:
            self.variant = ObjectVariant.objects.get(slug=self.trigger)
            for f in self.variant.filters.filter(collection_slug=self.collection.slug).select_related('filter_name'):
                self.tags_list.append(sorted(f.tags))
                for t in f.tags:
                    self.prefixes_set.add(t.split(':')[0])
                if not self.default_tags and f.filter_name.default:
                    self.default_tags = f.tags
        except ObjectVariant.DoesNotExist:
            self.variant = None

    def exists(self):
        return self.variant is not None

    def get_data(self):
        return self.variant

    def get_default_tags(self):
        return self.default_tags

    def check_tags(self, tags):
        _tags = sorted([t for t in tags if t.split(':')[0] in self.prefixes_set])
        for t in self.tags_list:
            if _tags == t:
                return True
        return False

    def get_default_url(self):
        from pcart_catalog.utils import normalize_filter_tags
        url = self.collection.get_absolute_url() + '/'.join(
            normalize_filter_tags(
                self.collection,
                tags=self.get_default_tags(),
                trigger=self.trigger,
            ))
        if not url.endswith('/'):
            url += '/'
        return url

    def get_prefixes(self):
        return list(self.prefixes_set)
