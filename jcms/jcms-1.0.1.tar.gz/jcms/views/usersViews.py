from django.contrib.auth.models import User
from jcms.mixins.jcms_crud import JcmsCrud


class UserViews(JcmsCrud):
    model = User
    create_edit_list = ['username', 'first_name', 'last_name', 'email', 'password', 'groups',
               'is_staff', 'is_active', 'is_superuser']
    list_fields = ['username', 'email', 'is_active']
