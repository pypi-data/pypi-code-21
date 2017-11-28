# -*- coding: utf-8 -*-

from trytond.model import ModelView, ModelSQL, ModelSingleton, fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from datetime import date
from trytond.transaction import Transaction

# objektklassen auflisten
__metaclass__ = PoolMeta
__all__ = ['Configuration']


class Configuration(ModelSingleton, ModelSQL, ModelView):
    'configuration'
    __name__ = 'periodic_invoice.configuration'

    holidays = fields.Text(string=u'Holidays', help=u'one date per line')
    company = fields.Many2One(model_name='company.company', string=u'Company', required=True,
                help=u'Choose the company for which the invoices should be created automatically.')

    @classmethod
    def __setup__(cls):
        super(Configuration, cls).__setup__()
        cls._error_messages.update({
            'cfgmsg_invalid_datescheme': (u"Invalid syntax of the date '%s'. (allowed: DD.MM. or DD.MM.YYYY)"),
        })

    @classmethod
    def convert_holidays(cls, htxt):
        """ check syntax and convert
        """
        l1 = htxt.split('\n')
        l2 = []
        for i in l1:
            t1 = i.strip()
            if len(t1) == 0:
                continue
            
            l3 = t1.split('.')
            if len(l3) == 3:
                if len(l3[2]) == 0:
                    y1 = str(date.today().year)
                else :
                    y1 = l3[2]
            else :
                cls.raise_user_error('cfgmsg_invalid_datescheme', (t1))
            
            # try to convert to a date
            try :
                y1 = int(y1)
                if not ((1990 <= y1) and (y1 <= 2100)):
                    cls.raise_user_error('cfgmsg_invalid_datescheme', (t1))
                m1 = int(l3[1])
                d1 = int(l3[0])
                dt1 = date(y1, m1, d1)
                if len(l3[2]) == 0:
                    l2.append('%02d.%02d.' % (d1, m1))
                else :
                    l2.append('%02d.%02d.%04d' % (d1, m1, y1))
            except :
                cls.raise_user_error('cfgmsg_invalid_datescheme', (t1))
        
        t_res = ''
        for i in l2:
            t_res += '%s\n' % i
        t_res = t_res[:-1]  # cut '\n'
        return t_res
        
    @fields.depends('holidays')
    def on_change_holidays(self):
        """ check syntax
        """
        Config = Pool().get('periodic_invoice.configuration')
        self.holidays = Config.convert_holidays(self.holidays)

    @classmethod
    def is_date_in_holidays(cls, date2check):
        """ check datetime.date() for holiday
        """
        if not isinstance(date2check, type(date.today())):
            raise ValueError(u'invalid data type')
            
        try :
            holidays = cls.get_singleton().holidays
        except :
            # no config - no holiday
            return False
        
        lst_hd = holidays.split('\n')
        for i in lst_hd:
            l1 = i.split('.')
            if len(l1) != 3:
                continue
            if len(l1[2]) == 0:
                y1 = date2check.year
            else :
                y1 = int(l1[2])
            m1 = int(l1[1])
            d1 = int(l1[0])

            # match holiday?
            if date2check == date(y1, m1, d1):
                return True
        return False
        
    @classmethod
    def updt_values(cls, vals):
        """ update some values on update or create
        """
        if 'holidays' in vals.keys():
            vals['holidays'] = cls.convert_holidays(vals['holidays'])

        if 'company' in vals:
            # update cron-user
            pool = Pool()
            ResUser = pool.get('res.user')
            ModelData = pool.get('ir.model.data')
            cron_user = ResUser(ModelData.get_id('periodic_invoice', 'user_cronjob_invoice'))
            tab_user = ResUser.__table__()
            cursor = Transaction().cursor

            updt_user = tab_user.update(
                        columns=[tab_user.company, tab_user.main_company],
                        values=[vals['company'], vals['company']],
                        where=(tab_user.id == cron_user.id)
                    )
            cursor.execute(*updt_user)
        return vals

    @classmethod
    def create(cls, vlist):
        """ create item
        """
        vlist = [x.copy() for x in vlist]
        for values in vlist:
            values = cls.updt_values(values)
        return super(Configuration, cls).create(vlist)

    @classmethod
    def write(cls, *args):
        """ save
        """
        actions = iter(args)
        for invtempl, values in zip(actions, actions):
            values = cls.updt_values(values)
        super(Configuration, cls).write(*args)

# ende Configuration
