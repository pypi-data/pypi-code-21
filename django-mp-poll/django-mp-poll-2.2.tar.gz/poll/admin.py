
from django.contrib import admin

from modeltranslation.admin import TranslationAdmin, TranslationTabularInline

from poll.models import Poll, PollChoice


class PollChoiceInline(TranslationTabularInline):

    model = PollChoice
    extra = 0
    min_num = 2


class PollAdmin(TranslationAdmin):

    inlines = [PollChoiceInline]

    list_display = ['question', 'created', 'votes']


admin.site.register(Poll, PollAdmin)
