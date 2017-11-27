from django.contrib.auth.models import Group
from jcms.mixins.jcms_crud import JcmsCrud


class GroupViews(JcmsCrud):
    model = Group
    create_edit_list = ['name', 'permissions']
    list_fields = create_edit_list
