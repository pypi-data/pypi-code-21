
from modeltranslation.translator import register, TranslationOptions

from flatpages.models import FlatPage


@register(FlatPage)
class FlatPageTranslationOptions(TranslationOptions):

    fields = ('title', 'meta_k', 'meta_d', 'content', )
