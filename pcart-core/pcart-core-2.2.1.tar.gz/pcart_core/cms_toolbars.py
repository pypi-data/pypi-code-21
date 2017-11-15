from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from cms.utils.urlutils import admin_reverse
from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool


@toolbar_pool.register
class PCartCoreToolbar(CMSToolbar):
    _pcart_menu = None

    def populate(self):
        if not self._pcart_menu:
            self._pcart_menu = self.toolbar.get_or_create_menu('pcart-core-menu', _('Core'))
            self._pcart_menu.add_sideframe_item(_('System info'), url=reverse('pcart_core:pcart-admin-system-info'))
            self._pcart_menu.add_sideframe_item(
                name=_('Theme settings'),
                url=admin_reverse('pcart_core_themesettings_changelist'),
            )
            self._pcart_menu.add_sideframe_item(
                name=_('Root files'),
                url=admin_reverse('pcart_core_rootfile_changelist'),
            )
