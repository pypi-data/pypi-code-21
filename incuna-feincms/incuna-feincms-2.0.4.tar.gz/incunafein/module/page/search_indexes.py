from haystack import indexes

from feincms.module.page.models import Page


class PageIndex(indexes.SearchIndex, indexes.Indexable):
    title = indexes.CharField(model_attr='title')
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Page

    def index_queryset(self):
        return self.get_model().objects.all()
