from django import template
from copy import copy
from molo.yourwords.models import (YourWordsCompetition, ThankYou,
                                   YourWordsCompetitionIndexPage)
from molo.core.templatetags.core_tags import get_pages

register = template.Library()


@register.inclusion_tag(
    'yourwords/your_words_competition_tag.html',
    takes_context=True
)
def your_words_competition(context):
    context = copy(context)
    locale_code = context.get('locale_code')
    main = context['request'].site.root_page
    page = YourWordsCompetitionIndexPage.objects.child_of(main).live().first()
    if page:
        competitions = (
            YourWordsCompetition.objects.child_of(page).filter(
                languages__language__is_main_language=True).specific())
    else:
        competitions = YourWordsCompetition.objects.none()

    context.update({
        'competitions': get_pages(context, competitions, locale_code)
    })
    return context


@register.inclusion_tag(
    'yourwords/your_words_competition_tag_for_section.html',
    takes_context=True
)
def your_words_competition_in_section(context, section):
    context = copy(context)
    locale_code = context.get('locale_code')
    page = section.get_main_language_page()
    if page:
        competitions = (
            YourWordsCompetition.objects.child_of(page).filter(
                languages__language__is_main_language=True).specific())
    else:
        competitions = YourWordsCompetition.objects.none()

    context.update({
        'competitions': get_pages(context, competitions, locale_code),
        'section': section
    })
    return context


@register.assignment_tag(takes_context=True)
def load_thank_you_page_for_competition(context, competition):

    page = competition.get_main_language_page()
    locale = context.get('locale_code')

    qs = ThankYou.objects.child_of(page).filter(
        languages__language__is_main_language=True)

    if not locale:
        return qs

    if qs:
        return get_pages(context, qs, locale)
    else:
        return []
