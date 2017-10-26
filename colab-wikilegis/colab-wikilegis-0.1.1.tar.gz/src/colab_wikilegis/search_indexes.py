from haystack import indexes
from colab_wikilegis import models


class WikilegisBillIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True,
                                  stored=False)
    type = indexes.EdgeNgramField()

    # Model fields
    title = indexes.EdgeNgramField(model_attr='title')
    epigraph = indexes.EdgeNgramField(model_attr='epigraph', null=True)
    description = indexes.EdgeNgramField(model_attr='description')
    status = indexes.EdgeNgramField(model_attr='get_status')
    theme = indexes.EdgeNgramField(model_attr='get_theme')
    url = indexes.EdgeNgramField(model_attr='get_url')

    def get_model(self):
        return models.WikilegisBill

    def prepare_type(self, obj):
        return u'bill'

    def index_queryset(self, using=None):
        return self.get_model().objects.exclude(status='draft')


class WikilegisSegmentIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True,
                                  stored=False)
    type = indexes.EdgeNgramField()

    # Model fields
    segment_type = indexes.EdgeNgramField(model_attr='get_segment_type')
    content = indexes.EdgeNgramField(model_attr='content')
    bill = indexes.EdgeNgramField(model_attr='get_bill')
    number = indexes.EdgeNgramField(model_attr='number', null=True)
    url = indexes.EdgeNgramField(model_attr='get_url')

    def get_model(self):
        return models.WikilegisSegment

    def prepare_type(self, obj):
        return u'segment'

    def index_queryset(self, using=None):
        return self.get_model().objects.exclude(bill__status='draft')


# class WikilegisCommentIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.EdgeNgramField(document=True, use_template=True,
#                                   stored=False)
#     type = indexes.EdgeNgramField()

#     # Model fields
#     author = indexes.EdgeNgramField(model_attr='get_author')
#     submit_date = indexes.DateTimeField(model_attr='submit_date')
#     content_type = indexes.EdgeNgramField(model_attr='content_type')
#     comment = indexes.EdgeNgramField(model_attr='comment')
#     parent = indexes.EdgeNgramField(model_attr='get_segment')
#     bill = indexes.EdgeNgramField(model_attr='get_bill')
#     url = indexes.EdgeNgramField(model_attr='get_url')

#     def get_model(self):
#         return models.WikilegisComment

#     def prepare_type(self, obj):
#         return u'comment'

#     def index_queryset(self, using=None):
#         draft_segments = models.WikilegisSegment.objects.filter(
#             bill__status='draft'
#         )
#         draft_segments = draft_segments.values_list('id', flat=True)
#         all_comments = self.get_model().objects.filter(content_type='segment')
#         return all_comments.exclude(object_pk__in=draft_segments)
