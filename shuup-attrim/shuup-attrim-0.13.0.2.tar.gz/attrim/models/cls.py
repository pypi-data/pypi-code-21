from django.db import models
from django.utils.translation import ugettext_lazy as _
from parler.utils.context import switch_language
from shuup.core.models import ProductType as ShuupProductType
from enumfields import EnumIntegerField
from parler.models import TranslatedFields
from parler.models import TranslatableModel

from attrim.models.type import Type
from attrim.trans_str import TransStr


class Class(TranslatableModel):
    product_type = models.ForeignKey(
        ShuupProductType,
        related_name='attrim_classes',
        related_query_name='attrim_cls',
    )
    code = models.SlugField(unique=True)

    type = EnumIntegerField(Type)

    translations = TranslatedFields(
        name=models.CharField(max_length=64, verbose_name=_('name')),
    )

    class JSONAPIMeta:
        resource_name = 'attrim-classes'

    def set_name(self, name: TransStr):
        for lang_code, name_translated in name:
            with switch_language(self, lang_code):
                self.name = name_translated
