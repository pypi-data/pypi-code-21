# Your models here.
from django.db import models
from django.conf import settings
from colab.plugins import helpers


class DiscourseCategory(models.Model):

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=50)
    text_color = models.CharField(max_length=50)
    slug = models.CharField(max_length=255)
    description = models.TextField(null=True)

    topic_count = models.IntegerField(default=0)
    post_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['name']


class DiscourseTopic(models.Model):

    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    category = models.ForeignKey('DiscourseCategory')

    created_at = models.DateTimeField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    last_poster_username = models.CharField(max_length=255)
    last_posted_at = models.DateTimeField()
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                          related_name='topics')

    views = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    posts_count = models.IntegerField(default=0)
    participant_count = models.IntegerField(default=0)

    visible = models.BooleanField(default=True)
    closed = models.BooleanField(default=False)

    def get_url(self):
        prefix = helpers.get_plugin_prefix('colab_discourse', regex=False)
        return '/{}t/{}/{}'.format(prefix, self.slug, self.id)

    def get_category_url(self):
        prefix = helpers.get_plugin_prefix('colab_discourse', regex=False)
        return '/{}c/{}'.format(prefix, self.category.slug)


class DiscoursePost(models.Model):
    id = models.IntegerField(primary_key=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    topic = models.ForeignKey('DiscourseTopic', related_name='posts')
    post_number = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    cooked = models.TextField()

    reply_count = models.IntegerField(default=0)
    quote_count = models.IntegerField(default=0)
    reads = models.IntegerField(default=0)

    def get_url(self):
        prefix = helpers.get_plugin_prefix('colab_discourse', regex=False)
        return '/{}t/{}/{}#post_{}'.format(prefix, self.topic.slug,
                                           self.topic_id, self.id)


class DiscourseBadgeType(models.Model):

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)


class DiscourseBadge(models.Model):

    id = models.IntegerField(primary_key=True)
    badge_type = models.ForeignKey('DiscourseBadgeType')
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    long_description = models.TextField()
    icon = models.CharField(max_length=255)
