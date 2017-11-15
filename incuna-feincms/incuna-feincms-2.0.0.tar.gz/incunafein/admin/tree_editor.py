from django.conf import settings as django_settings
from django.utils.translation import ugettext_lazy as _
from feincms.admin.tree_editor import *


class TreeEditor(TreeEditor):
    def _actions_column(self, instance):
        actions = super(TreeEditor, self)._actions_column(instance)
        static_url = django_settings.STATIC_URL

        opts = instance._meta
        if hasattr(opts, 'parent_attr'):
            actions.insert(0, u'<a href="add/?%s=%s" title="%s"><img src="%simg/admin/icon_addlink.gif" alt="%s"></a>' % (
                opts.parent_attr, instance.pk, _('Add child'), static_url, _('Add child')))
            actions.insert(0, u'<a href="%s" title="%s"><img src="%simg/admin/selector-search.gif" alt="%s" /></a>' % (
                instance.get_absolute_url(), _('View on site'), static_url, _('View on site')))
        return actions
