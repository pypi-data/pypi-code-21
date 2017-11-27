from jcms.models import Option
from jcms.mixins.jcms_crud import JcmsCrud


class OptionViews(JcmsCrud):
    model = Option
    create_edit_list = ['type', 'value']
    list_fields = create_edit_list
