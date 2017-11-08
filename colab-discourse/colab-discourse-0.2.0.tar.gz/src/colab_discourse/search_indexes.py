from haystack import indexes
from colab_discourse import models


class DiscourseTopicIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True,
                                  stored=False)
    type = indexes.EdgeNgramField()

    # Model fields
    title = indexes.EdgeNgramField(model_attr='title')
    category = indexes.EdgeNgramField(model_attr='category__name')
    category_color = indexes.CharField(model_attr='category__color')
    category_text_color = indexes.CharField(model_attr='category__text_color')
    created_at = indexes.DateTimeField(model_attr='created_at')
    created_by = indexes.EdgeNgramField(model_attr='created_by__username')
    last_posted_at = indexes.DateTimeField(model_attr='last_posted_at')
    views = indexes.IntegerField(model_attr='views')
    like_count = indexes.IntegerField(model_attr='like_count')
    posts_count = indexes.IntegerField(model_attr='posts_count')
    participant_count = indexes.IntegerField(model_attr='participant_count')
    visible = indexes.BooleanField(model_attr='visible')
    closed = indexes.BooleanField(model_attr='closed')
    url = indexes.EdgeNgramField(model_attr='get_url')

    def get_model(self):
        return models.DiscourseTopic

    def prepare_type(self, obj):
        return u'topic'

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(visible=True)


class DiscoursePostIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True,
                                  stored=False)
    type = indexes.EdgeNgramField()

    # Model fields
    author = indexes.EdgeNgramField(model_attr='author__username')
    topic = indexes.EdgeNgramField(model_attr='topic__title')
    cooked = indexes.EdgeNgramField(model_attr='cooked')
    created_at = indexes.DateTimeField(model_attr='created_at')
    updated_at = indexes.DateTimeField(model_attr='updated_at')
    reply_count = indexes.IntegerField(model_attr='reply_count')
    quote_count = indexes.IntegerField(model_attr='quote_count')
    reads = indexes.IntegerField(model_attr='reads')
    url = indexes.EdgeNgramField(model_attr='get_url')

    def get_model(self):
        return models.DiscoursePost

    def prepare_type(self, obj):
        return u'post'

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(topic__visible=True)
