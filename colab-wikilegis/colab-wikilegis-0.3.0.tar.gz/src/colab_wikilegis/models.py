# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from colab.accounts.models import User
from colab.plugins import helpers


BILL_STATUS_CHOICES = (
    ('draft', _('Draft')),
    ('published', _('Published')),
    ('closed', _('Closed'))
)


class WikilegisBillTheme(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50)


class WikilegisBill(models.Model):

    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=999)
    epigraph = models.CharField(max_length=999, null=True)
    description = models.CharField(max_length=999)
    status = models.CharField(max_length=999,
                              choices=BILL_STATUS_CHOICES, default='1')
    theme = models.ForeignKey('WikilegisBillTheme', null=True)
    closing_date = models.DateField(null=True, blank=True)
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField(editable=False)

    votes_count = models.IntegerField()
    upvote_count = models.IntegerField()
    downvote_count = models.IntegerField()
    comments_count = models.IntegerField()
    amendments_count = models.IntegerField()

    def get_url(self):
        prefix = helpers.get_plugin_prefix('colab_wikilegis', regex=False)
        return '/{}bill/{}'.format(prefix, self.id)

    def get_status(self):
        return self.get_status_display()

    def get_theme(self):
        return self.theme.description


class WikilegisSegmentType(models.Model):

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=999)
    presentation_name = models.CharField(max_length=999)


class WikilegisSegment(models.Model):

    id = models.IntegerField(primary_key=True)
    bill = models.ForeignKey('WikilegisBill', related_name='segments')
    segment_type = models.ForeignKey('WikilegisSegmentType')
    number = models.PositiveIntegerField(default=0, null=True, blank=True)
    content = models.TextField()
    created = models.DateTimeField(editable=False, auto_now_add=True)
    modified = models.DateTimeField(editable=False, auto_now=True)

    def get_segment_type(self):
        return self.segment_type.name

    def get_bill(self):
        return self.bill.title

    def get_url(self):
        prefix = helpers.get_plugin_prefix('colab_wikilegis', regex=False)
        return '/{}bill/{}/amendments/{}#tab_edit'.format(prefix, self.bill_id, self.id)


# class WikilegisComment(models.Model):

#     id = models.IntegerField(primary_key=True)
#     user = models.ForeignKey(settings.AUTH_USER_MODEL)
#     submit_date = models.DateTimeField()
#     content_type = models.CharField(max_length=999)
#     object_pk = models.IntegerField()
#     comment = models.TextField()

#     def get_author(self):
#         user = User.objects.get(pk=self.user_id)
#         return user.username

#     def get_parent_object(self):
#         parent_obj = None
#         if self.content_type == 'segment':
#             parent_obj = WikilegisSegment.objects.get(pk=self.object_pk)

#         return parent_obj

#     def get_segment(self):
#         parent = self.get_parent_object()
#         return parent.get_segment_type()

#     def get_bill(self):
#         parent = self.get_parent_object()
#         return parent.bill.title

#     def get_url(self):
#         parent = self.get_parent_object()
#         return '{}#c{}'.format(parent.get_url(), self.id)
