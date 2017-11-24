from django.utils.translation import ugettext_lazy as _

from shuup.admin.base import AdminModule
from shuup.admin.base import MenuEntry
from shuup.admin.menu import PRODUCTS_MENU_CATEGORY
from shuup.admin.utils.urls import derive_model_url
from shuup.admin.utils.urls import admin_url
from shuup.admin.utils.urls import get_edit_and_list_urls
from shuup.admin.utils.permissions import get_default_model_permissions

from typing import List

from attrim.models import Class


class ClassModule(AdminModule):
    name = 'Attrim'
    breadcrumbs_menu_entry = MenuEntry(name, url='shuup_admin:attrim.list')

    def get_urls(self) -> list:
        """
        Composes default urls with help of shuup func `get_edit_and_list_urls`
        and also adds `delete_url` to `urls` list.
        
        At the moment shuup does not have a function like
        `get_edit_and_list_urls` for **delete** url.
        """
        urls = []

        edit_and_list_urls = get_edit_and_list_urls(
            url_prefix='^attrim',
            view_template='attrim.admin.cls.views.Class%sView',
            name_template='attrim.%s',
        )
        urls += edit_and_list_urls

        delete_url = admin_url(
            regex='^attrim/(?P<pk>\d+)/delete$',
            view='attrim.admin.cls.views.ClassDeleteView',
            name='attrim.delete',
        )
        urls.append(delete_url)

        return urls

    def get_menu_entries(self, request) -> List[MenuEntry]:
        return [
            MenuEntry(
                text=_('Attrim'),
                icon='fa fa-asterisk',
                url='shuup_admin:attrim.list',
                category=PRODUCTS_MENU_CATEGORY,
            ),
        ]

    # noinspection PyShadowingBuiltins
    def get_model_url(self, object, kind) -> object:
        return derive_model_url(
            model_class=Class,
            urlname_prefix='shuup_admin:attrim',
            object=object,
            kind=kind,
        )

    def get_required_permissions(self) -> set:
        return get_default_model_permissions(Class)
