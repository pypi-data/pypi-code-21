
from modeltranslation.translator import register, TranslationOptions

from poll.models import Poll, PollChoice


@register(Poll)
class ArticleTranslationOptions(TranslationOptions):

    fields = ('question', )


@register(PollChoice)
class ArticleTagTranslationOptions(TranslationOptions):

    fields = ('value', )
