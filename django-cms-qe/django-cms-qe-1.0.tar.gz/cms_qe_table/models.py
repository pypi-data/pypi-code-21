from typing import List, Union

from cms.models.pluginmodel import CMSPlugin
from django.core.paginator import Paginator, Page, EmptyPage, PageNotAnInteger
from django.db import models
from django.db.models.base import ModelBase
from django.utils.translation import ugettext as _
from jsonfield import JSONField

from .exceptions import TableDoesNotExists
from .utils import get_model_by_table


class TablePluginModel(CMSPlugin):
    """
    Configuration model for plugin Table for Django CMS QE. Possibility to specify
    table, columns, order, filtering etc. etc.
    """

    table = models.CharField(max_length=100, verbose_name=_('Table to show'))
    columns = JSONField(verbose_name=_('Columns to show'))
    paging_show = models.BooleanField(default=True, verbose_name=_('Show paging'))
    paging_per_page = models.IntegerField(default=20, verbose_name=_('How many items per page when paging'))

    def __str__(self):
        if self.table_exists:
            return '{m.app_label} / {m.object_name}'.format(m=self.model._meta)
        return _('Non existing table {}.').format(self.table)

    @property
    def table_exists(self) -> bool:
        """
        Returns if table exists. When programmer move model or rename table
        without change in this configuration, it will not be available anymore.
        """
        try:
            get_model_by_table(self.table)
            return True
        except TableDoesNotExists:
            return False

    @property
    def columns_exist(self) -> bool:
        """
        Returns if all columns exists. When programmer rename column
        without change in this configuration, it will not be available anymore.
        """
        if not self.table_exists:
            return False
        model = self.model
        # pylint:disable=not-an-iterable
        if not all(hasattr(model, column) for column in self.columns):
            return False
        return True

    @property
    def model(self) -> ModelBase:
        """
        Returns model for configured table.
        """
        return get_model_by_table(self.table)

    def get_header(self) -> List[str]:
        """
        Returns header for table with ``verbose_name`` of fields if exists.
        In other cases at least uses name of that field.
        """
        def f(column):
            field = self.model._meta.get_field(column)
            return getattr(field, 'verbose_name', field.name)
        return [f(column) for column in self.columns]  # pylint: disable=not-an-iterable

    def get_items(self, page: Union[int, str] = None) -> Page:
        """
        Returns items for table without header. It's simply list (items)
        of lists (columns), not whole objects. Header is not included,
        for that use :any:`TablePluginModel.get_header`.
        """
        items_list = self.model.objects.all()
        if not self.paging_show:
            return self._get_items(items_list)

        paginator = Paginator(items_list, self.paging_per_page)

        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)

        # Evaluate query and return only needed columns.
        items.object_list = self._get_items(items)
        return items

    def _get_items(self, items: List[ModelBase]) -> List[List[str]]:
        return [
            [getattr(item, column, '') for column in self.columns]  # pylint: disable=not-an-iterable
            for item in items
        ]
