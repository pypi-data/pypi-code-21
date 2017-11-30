from enumfields import Enum
from django.utils.translation import ugettext_lazy as _


class Type(Enum):
    INT = 1
    DECIMAL = 3

    TRANS_STR = 20
    STR = 21

    class Labels:
        # Translators: attrim type labels
        INT = _('integer')
        DECIMAL = _('decimal')

        TRANS_STR = _('translated string')
        STR = _('string')
