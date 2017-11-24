from django.utils.translation import ugettext_lazy as _

from .export import register_export_action


register_export_action('csv', _('Export selected as CSV'))
register_export_action('xls', _('Export selected as XLS'))
register_export_action('json', _('Export selected as JSON'))
register_export_action('html', _('Export selected as HTML'))
