import json

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import admin
from django.conf.urls import url
from django.core.urlresolvers import reverse
from django.template.defaultfilters import truncatechars
from django.shortcuts import get_object_or_404, redirect
from django import forms
import csv
from django.http import HttpResponse

from wagtail.wagtailcore.utils import cautious_slugify

from molo.core.models import ArticlePage
from molo.yourwords.models import (YourWordsCompetitionEntry,
                                   YourWordsCompetition,
                                   YourWordsCompetitionIndexPage)


def download_as_csv(YourWordsCompetitionEntryAdmin, request, queryset):
    opts = queryset.model._meta
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename=export.csv'
    writer = csv.writer(response)
    field_names = [field.name for field in opts.fields]
    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])
    return response


download_as_csv.short_description = "Download selected as csv"


@staff_member_required
def convert_to_article(request, entry_id):
    def get_entry_author(entry):
        written_by_user = 'Written by: %s' % entry.user.username
        written_by_anon = 'Written by: Anonymous'
        if entry.hide_real_name:
            return written_by_anon
        return written_by_user

    entry = get_object_or_404(YourWordsCompetitionEntry, pk=entry_id)
    if not entry.article_page:
        competition_index_page = (
            YourWordsCompetitionIndexPage.objects.live().first())
        article = ArticlePage(
            title=entry.story_name,
            slug='yourwords-entry-%s' % cautious_slugify(entry.story_name),
            body=json.dumps([
                {"type": "paragraph", "value": get_entry_author(entry)},
                {"type": "paragraph", "value": entry.story_text}
            ])
        )
        competition_index_page.add_child(instance=article)
        article.save_revision()
        article.unpublish()

        entry.article_page = article
        entry.save()
        return redirect('/admin/pages/%d/move/' % article.id)
    return redirect('/admin/pages/%d/edit/' % entry.article_page.id)


class YourWordsCompetitionEntryForm(forms.ModelForm):

    class Meta:
        model = YourWordsCompetitionEntry
        fields = ['story_name', 'story_text', 'user', 'hide_real_name',
                  'is_read', 'is_shortlisted', 'is_winner']


class YourWordsCompetitionEntryAdmin(admin.ModelAdmin):
    list_display = ['story_name', 'truncate_text', 'user', 'hide_real_name',
                    'submission_date', 'is_read', 'is_shortlisted',
                    'is_winner', '_convert']
    list_filter = ['competition__slug', 'is_read', 'is_shortlisted',
                   'is_winner', 'submission_date']
    list_editable = ['is_read', 'is_shortlisted', 'is_winner']
    date_hierarchy = 'submission_date'
    form = YourWordsCompetitionEntryForm
    readonly_fields = ('competition', 'story_name', 'story_text', 'user',
                       'hide_real_name', 'submission_date')
    actions = [download_as_csv]

    def truncate_text(self, obj, *args, **kwargs):
        return truncatechars(obj.story_text, 30)

    def get_urls(self):
        urls = super(YourWordsCompetitionEntryAdmin, self).get_urls()
        entry_urls = [
            url(r'^(?P<entry_id>\d+)/convert/$', convert_to_article),
        ]
        return entry_urls + urls

    def _convert(self, obj, *args, **kwargs):
        if obj.article_page:
            return (
                '<a href="/admin/pages/%d/edit/">Article Page</a>' %
                obj.article_page.id)
        return (
            ' <a href="%d/convert/" class="addlink">Convert to article</a>' %
            obj.id)

    _convert.allow_tags = True
    _convert.short_description = ''


class YourWordsCompetitionAdmin(admin.ModelAdmin):
    list_display = ['entries', 'start_date', 'end_date', 'status',
                    'number_of_entries']
    list_filter = ['title', 'start_date', 'end_date']
    search_fields = ['title', 'content', 'description']
    date_hierarchy = 'start_date'

    def number_of_entries(self, obj, *args, **kwargs):
        return YourWordsCompetitionEntry.objects.filter(
            competition__slug=obj.slug).count()

    def status(self, obj, *args, **kwargs):
        if obj.live:
            return 'First published on ' + str(obj.first_published_at.date())
        return 'Unpublished'

    def entries(self, obj, *args, **kwargs):
        url = reverse('admin:yourwords_yourwordscompetitionentry_changelist')
        return '<a href="%s?competition__slug=%s">%s</a>' % (
            url, obj.slug, obj)

    entries.allow_tags = True
    entries.short_description = 'Title'


admin.site.register(YourWordsCompetitionEntry, YourWordsCompetitionEntryAdmin)
admin.site.register(YourWordsCompetition, YourWordsCompetitionAdmin)
