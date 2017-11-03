
from modeltranslation.translator import register, TranslationOptions

from seo.models import PageMeta


@register(PageMeta)
class PageMetaTranslationOptions(TranslationOptions):

    fields = ('title', 'keywords', 'description', 'breadcrumb', 'header', )
