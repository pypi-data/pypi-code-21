from django.template import Context
from django.utils.translation import ugettext_lazy as _
from shuup.admin.utils.picotable import Column
from shuup.admin.utils.picotable import TextFilter
from shuup.admin.utils.views import PicotableListView

from attrim.models import Class


class ClassListView(PicotableListView):
    model = Class

    default_columns = [
        Column(
            'code',
            _('Code'),
            sort_field='code',
            display='code',
            filter_config=TextFilter(
                filter_field='code',
                placeholder=_('Filter by code...'),
            ),
        ),
        Column(
            'product_type',
            _('Product type'),
            sort_field='product_type',
            display='product_type',
            filter_config=TextFilter(
                filter_field='product_type',
                placeholder=_('Filter by product type...'),
            ),
        ),
    ]

    def get_context_data(self, **kwargs) -> Context:
        context = super().get_context_data(**kwargs)
        self.model._meta.verbose_name = _('Attribute class')
        self.model._meta.verbose_name_plural = _('Attribute classes')
        return context
