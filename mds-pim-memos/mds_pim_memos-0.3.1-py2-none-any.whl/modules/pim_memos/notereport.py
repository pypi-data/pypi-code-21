# -*- coding: utf-8 -*-

from trytond.pool import Pool, PoolMeta
from trytond.report import Report
from datetime import date


__all__ = ['ReportOdt']
__metaclass__ = PoolMeta


class ReportOdt(Report):
    __name__ = 'pim_memos.reportodt'

    @classmethod
    def execute(cls, ids, data):
        """ edit filename
        """
        ExpObj = Pool().get(data['model'])(data['id'])
        (ext1, cont1, dirprint, titel) = super(ReportOdt, cls).execute(ids, data)
        titel = '%s-note-%s' % (date.today().strftime('%Y%m%d'), ExpObj.name[:15])
        return (ext1, cont1, dirprint, titel)

    @classmethod
    def get_context(cls, records, data):
        report_context = super(ReportOdt, cls).get_context(records, data)
        report_context['islastitem'] = cls.is_last_item
        return report_context
 
    @classmethod
    def is_last_item(cls, liste, item):
        """ check if 'item' is the last in 'liste'
        """
        if liste[-1].id == item.id:
            return True
        else :
            return False

# ende ReportOdt

