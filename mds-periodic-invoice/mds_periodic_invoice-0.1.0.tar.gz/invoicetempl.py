# -*- coding: utf-8 -*-

from trytond.model import ModelView, ModelSQL, fields, Unique, Check
from trytond.pool import Pool, PoolMeta
from trytond.pyson import If, Eval, Bool, Id, Or
from datetime import date, timedelta
from sql import Null
from sql.functions import CurrentDate
from sql.conditionals import Case
from dateutil import rrule
from decimal import Decimal
from trytond.transaction import Transaction
from trytond.modules.account_invoice.invoice import _TYPE as INV_TYPES,\
        _TYPE2JOURNAL as INV_TYPE2JOURNAL
from constrepeat import *
from trytond.modules.product import price_digits

__all__ = ['InvoiceTemplate', 'InvoicesRel', 'InvoiceLine', 'InvoiceLineTax']
__metaclass__ = PoolMeta


sel_stopcond = [
        (STOPCOND_NEVER, u'do not stop'),
        (STOPCOND_BYCOUNT, u"stop after 'number of calls' repeats"),
        (STOPCOND_BYENDDATE, u"stop at 'end date'")
    ]

sel_intervalunit = [
        (REPEAT_DAILY, 'day'),
        (REPEAT_WEEKLY, 'week'),
        (REPEAT_MONTHLY, 'month'),
        (REPEAT_YEARLY, 'year'),
    ]

sel_invdate = [
        (INVDATE_CREATEDATE, u'create date'),
        (INVDATE_1ST_CURRENT_MONTH, u'the first of the current month'),
        (INVDATE_1ST_DAY_OF_PREVMONTH, u'first day in the previous month'),
        (INVDATE_1ST_WORKDAY_PREVMONTH, u'first working day in the previous month'),
        (INVDATE_1ST_WORKDAY_CURRMONTH, u'first working day in the current month'),
        (INVDATE_LAST_DAY_CURRMONTH, u'the last day in the current month'),
        (INVDATE_LAST_DAY_CURRYEAR, u'last day in the current year'),
        (INVDATE_LAST_DAY_PREVMONTH, u'last day in the previous month'),
        (INVDATE_LAST_DAY_PREVYEAR, u'last day in the previous year'),
        (INVDATE_LAST_WORKDAY_CURRMONTH, u'last working day in the current month'),
        (INVDATE_LAST_WORKDAY_CURRYEAR, u'last working day in the current year'),
        (INVDATE_LAST_WORKDAY_PREVMONTH, u'last working day in the previous month'),
        (INVDATE_LAST_WORKDAY_PREVYEAR, u'last working day in the previous year'),
        (INVDATE_CREATEDATE_MINUS1, u'create date minus 1 day'),
        (INVDATE_CREATEDATE_MINUS2, u'create date minus 2 days'),
        (INVDATE_CREATEDATE_MINUS3, u'create date minus 3 days'),
        (INVDATE_CREATEDATE_MINUS4, u'create date minus 4 days'),
    ]

LINETYP_LINE = 'line'
LINETYP_SUBTOTAL = 'subtotal'
LINETYP_TITLE = 'title'
LINETYP_COMMENT = 'comment'
sel_invline_type = [
        (LINETYP_LINE, 'Line'),
        (LINETYP_SUBTOTAL, 'Subtotal'),
        (LINETYP_TITLE, 'Title'),
        (LINETYP_COMMENT, 'Comment'),
    ]
    
TARGSTATE_DRAFT = 'draft'
TARGSTATE_VALIDATED = 'valid'
TARGSTATE_POSTED = 'post'
TARGSTATE_MAILED = 'mail'
sel_targstate = [
        (TARGSTATE_DRAFT, u'Draft'),
        (TARGSTATE_VALIDATED, u'Validated'),
        (TARGSTATE_POSTED, u'Posted'),
#        (TARGSTATE_MAILED, u'sent by mail'),
    ]


# list of placeholders to customize the invoices
# for template
list_placeholder_templ = [
        ('startdate','date_start', u'Start date', '%s', [], None),
        ('enddate','date_end', u'End date', '%s', [], None),
        ('email','email', u'E-Mail', '%s', [], None),
        
    ]
# for new invoice
list_placeholder_invnew = [
        ('invoicedate','invoice_date', u'Invoice Date', '%s', [], None),
        ('paymentterm','payment_term', u'Payment Term', '%s', [], 'name'),
        ('untaxed','untaxed_amount', u'Untaxed', '%s', [], None),
        ('tax','tax_amount', u'Tax', '%s', [], None),
        ('total','total_amount', u'Total', '%s', [], None),
    ]


_ZERO = Decimal('0.0')


class InvoiceTemplate(ModelSQL, ModelView):
    'InvoiceTemplate'
    __name__ = 'periodic_invoice.invoice'

    active = fields.Boolean(string=u'Active', select=True, states={'invisible': True})
    active2 = fields.Boolean(string=u'Active', select=True,
                help=u'When activated, the invoice is created at the next time.')
    name = fields.Char(string=u'Title', help=u'Title of the invoice template', required=True, select=True)
    desc = fields.Text(string=u'Description')
    
    # recurring rule
    runatweekday = fields.Boolean(string=u'weekdays only', 
                help=u'move execution date to a working day')
    date_start = fields.Date(string=u'Start date', required=True, select=True,
                help=u'Select the start date to calculate the next execution time.',
                states={
                    'readonly': Eval('active2', False) == False,
                }, depends=['active2'])
    date_end = fields.Date(string=u'End date', select=True,
                states={
                    'required': Eval('stopcondition', '') == STOPCOND_BYENDDATE,
                    'invisible': Eval('stopcondition', '') != STOPCOND_BYENDDATE,
                    'readonly': Eval('active2', False) == False,
                }, depends=['stopcondition','active2'],
                help=u'Select the end date to stop the creation of invoices.')
    intervalunit = fields.Selection(string=u'Interval unit', selection=sel_intervalunit,
                help=u'Select the interval unit to determine the next execution date.',
                required=True, select=True, sort=False,
                states={
                    'readonly': Eval('active2', False) == False,
                }, depends=['active2'])
    intervalnumber = fields.Integer(string=u'Interval number', required=True, select=True,
                states={
                    'readonly': Eval('active2', False) == False,
                }, depends=['active2'])
    stopcondition = fields.Selection(string=u'Stop condition', selection=sel_stopcond, 
                required=True, select=True, sort=False,
                states={
                    'readonly': Eval('active2', False) == False,
                }, depends=['active2'])
    calls_to_go = fields.Integer(string=u'Number of calls', select=True,
                help=u"Disables the repeat function after 'Number of calls'.",
                states={
                    'invisible': Eval('stopcondition', '') != STOPCOND_BYCOUNT,
                    'required': Eval('stopcondition', '') == STOPCOND_BYCOUNT,
                    'readonly': Eval('active2', False) == False,
                }, depends=['stopcondition', 'active2'])
    calls_done = fields.Integer(string=u'Calls done', select=True, readonly=True, 
                states={
                    'invisible': Eval('stopcondition', '') != STOPCOND_BYCOUNT,
                    'readonly': Eval('active2', False) == False,
                }, depends=['stopcondition', 'active2'])
    calls_donetotal = fields.Integer(string=u'Total number of calls', readonly=True)
    date_lastrun = fields.Date(string=u'last call date', readonly=True)
    date_nextrun = fields.Date(string=u'Next call date', readonly=True)

    # target state
    targstate = fields.Selection(string=u'Target state', selection=sel_targstate, sort=False,
                help=u'State of the invoice after the automatic create', required=True)
    email = fields.Char(string=u'E-Mail', help=u'E-mail address for sending the invoice',
                states={
                    'required': Eval('targstate', '') == TARGSTATE_MAILED,
                }, depends=['targstate'])
    
    # invoice
    party = fields.Many2One(model_name='party.party', string=u'Party', required=True, 
                select=True, ondelete='RESTRICT')
    invoice_address = fields.Many2One(model_name='party.address', string=u'Invoice Address', 
                required=True, depends=['party'], domain=[('party', '=', Eval('party'))])
    invdesc = fields.Char(string=u'Description', required=True,
                help=u'Description for the generated invoice')
    invdate = fields.Selection(string=u'Invoice date', required=True, 
                selection=sel_invdate)
    reference = fields.Char('Reference')
    journal = fields.Many2One(model_name='account.journal', string=u'Journal', required=True)
    invtype = fields.Selection(selection=INV_TYPES, string=u'Type', select=True, required=True)
    payment_term = fields.Many2One(model_name='account.invoice.payment_term', string=u'Payment Term', required=True)
    company = fields.Many2One(model_name='company.company', string=u'Company', required=True,
                select=True, domain=[
                        ('id', If(Eval('context', {}).contains('company'), '=', '!='),
                            Eval('context', {}).get('company', -1)),
                    ])
    account = fields.Many2One(model_name='account.account', string=u'Account', required=True,
                depends=['invtype', 'company'],
                domain=[
                    ('company', '=', Eval('company', -1)),
                    If(Eval('invtype').in_(['out_invoice', 'out_credit_note']),
                        ('kind', '=', 'receivable'),
                        ('kind', '=', 'payable')
                    ),
                ])
    currency = fields.Many2One(model_name='currency.currency', string=u'Currency', 
                required=True, states={'readonly': (Eval('lines', [0]) & Eval('currency')),})
    currency_digits = fields.Function(fields.Integer(string=u'Currency Digits'),
                'on_change_with_currency_digits')

    # amounts
    untaxed_amount = fields.Function(fields.Numeric(string=u'Untaxed',
                digits=(16, Eval('currency_digits', 2)), depends=['currency_digits']), 'get_amount')
    tax_amount = fields.Function(fields.Numeric(string=u'Tax', 
                digits=(16, Eval('currency_digits', 2)), depends=['currency_digits']), 'get_amount')
    total_amount = fields.Function(fields.Numeric(string=u'Total', 
                digits=(16, Eval('currency_digits', 2)), depends=['currency_digits']), 'get_amount')

    # invoices
    invoices = fields.Many2Many(relation_name='periodic_invoice.invoices_rel',
                    help=u'Invoices created from this template', readonly=True,
                    origin='invtempl', target='invoice', string=u'Invoices')
    lines = fields.One2Many(model_name='periodic_invoice.invline', 
                field='invoice', string=u'Lines')

    # functions
    nextrun = fields.Function(fields.Date(string=u'Next call date', readonly=True), 'get_nextrun')

    @classmethod
    def __setup__(cls):
        super(InvoiceTemplate, cls).__setup__()
        cls._order.insert(0, ('date_nextrun', 'ASC'))
        cls._order.insert(0, ('active2', 'DESC'))
        tab_inv = cls.__table__()
        cls._buttons.update({
            'btn_create_invoice': {},
            })
        cls._sql_constraints.extend([
            ('date_end', Check(tab_inv, (tab_inv.date_end > tab_inv.date_start) | (tab_inv.date_end == None)), 
            u"The value 'end date' must be after 'start date' or empty."),
            ('range_stopcondition', Check(tab_inv, tab_inv.stopcondition.in_([STOPCOND_NEVER, STOPCOND_BYCOUNT, STOPCOND_BYENDDATE])), 
            u"Invalid value in 'stop condition'."),
            ('range_intervalnumber', Check(tab_inv, tab_inv.intervalnumber > 0), 
            u'Interval number must be greater than zero.'),
            ('range_intervalunit', 
            Check(tab_inv, tab_inv.intervalunit.in_([REPEAT_DAILY, REPEAT_WEEKLY, REPEAT_MONTHLY, REPEAT_YEARLY])), 
            u"Invalid value in 'interval unit'."),
            ('range_calls_to_go', Check(tab_inv, (tab_inv.calls_to_go > 0) | (tab_inv.calls_to_go == None)), 
            u"The value 'calls to go' must be greater than 0 or empty."),
            ])

    @classmethod
    @ModelView.button        
    def btn_create_invoice(cls, items):
        """ create invoice by click
        """
        for i in items:
            cls.do_create_invoice(i, targedmode=TARGSTATE_DRAFT)

    @classmethod
    def default_runatweekday(cls):
        """ default: runatweekday
        """
        return False

    @classmethod
    def default_targstate(cls):
        """ default: targstate
        """
        return TARGSTATE_DRAFT

    @classmethod
    def default_active2(cls):
        """ default: active
        """
        return True

    @classmethod
    def default_intervalnumber(cls):
        """ defaul number
        """
        return 1
        
    @classmethod
    def default_stopcondition(cls):
        """ default: stopcondition
        """
        return STOPCOND_NEVER

    @classmethod
    def default_calls_to_go(cls):
        """ default: calls_to_go
        """
        return 1

    @classmethod
    def default_calls_done(cls):
        """ default: calls_done
        """
        return 0
        
    @classmethod
    def default_calls_donetotal(cls):
        """ default: calls_donetotal
        """
        return 0
        
    @classmethod
    def default_intervalunit(cls):
        """ repeat default
        """
        return REPEAT_MONTHLY

    @classmethod
    def default_date_start(cls):
        """ default: date_start
        """
        return date.today() + timedelta(days=5)
        
    @staticmethod
    def default_invdate():
        """ default: invdate
        """
        return INVDATE_1ST_WORKDAY_CURRMONTH
        
    @staticmethod
    def default_invtype():
        """ default: invtype
        """
        return Transaction().context.get('type', 'out_invoice')

    @staticmethod
    def default_currency():
        """ default: currency
        """
        Company = Pool().get('company.company')
        if Transaction().context.get('company'):
            company = Company(Transaction().context['company'])
            return company.currency.id

    @staticmethod
    def default_company():
        """ default: company
        """
        return Transaction().context.get('company')

    @classmethod
    def default_payment_term(cls):
        """ default: payment term
        """
        PaymentTerm = Pool().get('account.invoice.payment_term')
        payment_terms = PaymentTerm.search(cls.payment_term.domain)
        if len(payment_terms) == 1:
            return payment_terms[0].id

    @fields.depends('currency')
    def on_change_with_currency_digits(self, name=None):
        if self.currency:
            return self.currency.digits
        return 2

    @fields.depends('intervalunit', 'intervalnumber','date_nextrun', 'date_start', 'active2', 'runatweekday')
    def on_change_runatweekday(self):
        """ update nextrun
        """
        self.on_change_intervalunit()
    
    @fields.depends('intervalunit', 'intervalnumber','date_nextrun', 'date_start', 'active2', 'runatweekday')
    def on_change_active2(self):
        """ update nextrun
        """
        self.on_change_intervalunit()

    @fields.depends('intervalunit', 'intervalnumber','date_nextrun', 'date_start', 'active2', 'runatweekday')
    def on_change_date_start(self):
        """ update nextrun
        """
        self.on_change_intervalunit()

    @fields.depends('intervalunit', 'intervalnumber','date_nextrun', 'date_start', 'active2', 'runatweekday')
    def on_change_intervalnumber(self):
        """ update nextrun
        """
        self.on_change_intervalunit()

    @fields.depends('intervalunit', 'intervalnumber','date_nextrun', 'date_start', 'active2', 'runatweekday')
    def on_change_intervalunit(self):
        """ update nextrun
        """
        InvTempl = Pool().get('periodic_invoice.invoice')
        
        if self.active2 == True:
            self.date_nextrun = InvTempl.get_date_byrule({
                    'intervalunit': self.intervalunit,
                    'intervalnumber': self.intervalnumber,
                    'date_start': self.date_start,
                    'runatweekday': self.runatweekday,
                })
        else :
            self.date_nextrun = None
        
    @fields.depends('stopcondition', 'date_end', 'date_start', 'calls_done')
    def on_change_stopcondition(self):
        """ handle stopcondition
        """
        if self.stopcondition != STOPCOND_BYENDDATE:
            self.date_end = None
        else :
            self.date_end = self.date_start + timedelta(days=14)
        if self.stopcondition == STOPCOND_BYCOUNT:
            self.calls_done = 0
        
    @fields.depends('active2', 'calls_done')
    def on_change_active(self):
        """ set 'calls_done' to zero
        """
        if self.active2 == True:
            self.calls_done = 0
        
    @fields.depends('calls_to_go', 'calls_done')
    def on_change_calls_to_go(self):
        """ set 'calls_done' to zero
        """
        self.calls_done = 0

    @fields.depends('party', 'payment_term', 'invtype', 'company', 'invoice_address', 'account')
    def on_change_party(self):
        """ party changed
        """
        self.invoice_address = None
        self.get_account_payment_term()

        if self.party:
            self.invoice_address = self.party.address_get(type='invoice')

    @fields.depends('invtype', 'party', 'company', 'account')
    def on_change_invtype(self):
        """ invoice type changed
        """
        Journal = Pool().get('account.journal')
        journals = Journal.search([
                    ('type', '=', INV_TYPE2JOURNAL.get(self.invtype or 'out_invoice', 'revenue')),
                    ], limit=1)
        if journals:
            self.journal, = journals
        self.get_account_payment_term()

    def get_account_payment_term(self):
        """ Return default account and payment term
        """
        self.account = None
        if self.party:
            if self.invtype in ('out_invoice', 'out_credit_note'):
                self.account = self.party.account_receivable
                if (self.invtype == 'out_invoice') and self.party.customer_payment_term:
                    self.payment_term = self.party.customer_payment_term
            elif self.invtype in ('in_invoice', 'in_credit_note'):
                self.account = self.party.account_payable
                if (self.invtype == 'in_invoice') and self.party.supplier_payment_term:
                    self.payment_term = self.party.supplier_payment_term
        if self.company and self.invtype in ('out_credit_note', 'in_credit_note'):
            if (self.invtype == 'out_credit_note') and self.company.party.customer_payment_term:
                self.payment_term = self.company.party.customer_payment_term
            elif (self.invtype == 'in_credit_note') and self.company.party.supplier_payment_term:
                self.payment_term = self.company.party.supplier_payment_term

    @classmethod
    def do_create_invoice(cls, item, targedmode=TARGSTATE_DRAFT):
        """ create a invoice
        """
        pool = Pool()
        Invoice = pool.get('account.invoice')
        InvLine = pool.get('account.invoice.line')
        
        invobj = Invoice()
        invobj.company = item.company
        invobj.type = item.invtype
        invobj.description = item.invdesc
        invobj.invoice_date = cls.get_invoice_date_by_createdate(item.invdate, date.today())
        invobj.party = item.party
        invobj.invoice_address = item.invoice_address
        invobj.payment_term = item.payment_term
        invobj.currency = item.currency
        invobj.journal = item.journal
        invobj.account = item.account
        invobj.save()
        
        # add lines
        lines = []
        for i in item.lines:
            lineobj = InvLine()
            lineobj.invoice_type = item.invtype
            lineobj.party = item.party
            lineobj.currency = item.currency
            lineobj.company = item.company
            lineobj.type = i.type
            lineobj.sequence = i.sequence
            lineobj.product = i.product
            lineobj.quantity = i.quantity
            lineobj.unit = i.unit
            lineobj.description = i.description
            lineobj.note = i.note
            lineobj.account = i.account
            lineobj.unit_price = i.unit_price
            l1 = []
            for k in i.taxes:
                l1.append(k)
            lineobj.taxes = l1
            lines.append(lineobj)
        invobj.lines = lines
        invobj.save()
        
        # work placeholder
        for i in invobj.lines:
            i.note = cls.replace_placeholder(item, invobj, i.note)
            i.description = cls.replace_placeholder(item, invobj, i.description)
            i.save()
        invobj.description = cls.replace_placeholder(item, invobj, item.invdesc)
        invobj.save()
        
        # workflow
        if targedmode == TARGSTATE_DRAFT:
            pass
        elif targedmode == TARGSTATE_VALIDATED:
            Invoice.validate_invoice([invobj])
        elif targedmode == TARGSTATE_POSTED:
            Invoice.validate_invoice([invobj])
            Invoice.post([invobj])
        elif targedmode == TARGSTATE_MAILED:
            pass
            
        # add invoice to 'invoices'
        l1 = list(item.invoices)
        l1.append(invobj)
        item.invoices = l1
        item.save()
        
    @classmethod
    def do_periodic_job(cls, itemlist):
        """ do the jobs
        """
        for i in itemlist:
            i.calls_donetotal += 1
            i.date_lastrun = date.today()
            
            # calculate next date
            i.date_nextrun = cls.get_date_byrule({
                    'intervalunit': i.intervalunit,
                    'date_start': i.date_start,
                    'intervalnumber': i.intervalnumber,
                    'runatweekday': i.runatweekday,
                })
            
            # disable?
            if i.stopcondition == STOPCOND_BYCOUNT:
                i.calls_done += 1
                if i.calls_done >= i.calls_to_go:
                    i.active2 = False
            elif i.stopcondition == STOPCOND_BYENDDATE:
                if i.date_nextrun >= i.date_end:
                    i.active2 = False
            i.save()
            cls.do_create_invoice(i, targedmode=i.targstate)

    @classmethod
    def cron_do_periodic_invoice(cls):
        """ do the job
        """
        lst_do = cls.search([
                ('active2', '=', True), 
                ('date_nextrun', '<=', date.today()),
            ])
        if len(lst_do) > 0:
            cls.do_periodic_job(lst_do)

    @classmethod
    def workday_forward(cls, dt1):
        """ calculate the workday
        """
        Config = Pool().get('periodic_invoice.configuration')
        while (not dt1.weekday() in [0, 1, 2, 3, 4]) or \
            (Config.is_date_in_holidays(dt1) == True):
            dt1 = dt1 + timedelta(days=1)
        return dt1

    @classmethod
    def get_invoice_date_by_createdate(cls, datemode, crdate):
        """ calculates the invoice-date by rule and create-date
        """
        def workday_backward(dt1):
            """ calculate the workday
            """
            Config = Pool().get('periodic_invoice.configuration')
            while (not dt1.weekday() in [0, 1, 2, 3, 4]) or \
                (Config.is_date_in_holidays(dt1) == True):
                dt1 = dt1 - timedelta(days=1)
            return dt1

        if datemode == INVDATE_CREATEDATE:
            return crdate
        elif datemode == INVDATE_CREATEDATE_MINUS1:
            return crdate - timedelta(days=1)
        elif datemode == INVDATE_CREATEDATE_MINUS2:
            return crdate - timedelta(days=2)
        elif datemode == INVDATE_CREATEDATE_MINUS3:
            return crdate - timedelta(days=3)
        elif datemode == INVDATE_CREATEDATE_MINUS4:
            return crdate - timedelta(days=4)
        elif datemode == INVDATE_1ST_DAY_OF_PREVMONTH:
            if crdate.month == 1:
                return date(crdate.year - 1, 12, 1)
            else :
                return date(crdate.year, crdate.month - 1, 1)
        elif datemode == INVDATE_1ST_WORKDAY_PREVMONTH:
            dt1 = cls.get_invoice_date_by_createdate(INVDATE_1ST_DAY_OF_PREVMONTH, crdate)
            return cls.workday_forward(dt1)
        elif datemode == INVDATE_LAST_DAY_PREVMONTH:
            dt1 = date(crdate.year, crdate.month, 1)
            return dt1 - timedelta(days=1)
        elif datemode == INVDATE_LAST_WORKDAY_PREVMONTH:
            dt1 = cls.get_invoice_date_by_createdate(INVDATE_LAST_DAY_PREVMONTH, crdate)
            return workday_backward(dt1)
        elif datemode == INVDATE_1ST_CURRENT_MONTH:
            return date(crdate.year, crdate.month, 1)
        elif datemode == INVDATE_1ST_WORKDAY_CURRMONTH:
            return cls.workday_forward(date(crdate.year, crdate.month, 1))
        elif datemode == INVDATE_LAST_DAY_CURRMONTH:
            if crdate.month == 12:
                dt1 = date(crdate.year + 1, 1, 1)
            else :
                dt1 = date(crdate.year, crdate.month + 1, 1)
            return dt1 - timedelta(days=1)
        elif datemode == INVDATE_LAST_WORKDAY_CURRMONTH:
            dt1 = cls.get_invoice_date_by_createdate(INVDATE_LAST_DAY_CURRMONTH, crdate)
            return workday_backward(dt1)
        elif datemode == INVDATE_LAST_DAY_CURRYEAR:
            return date(crdate.year, 12, 31)
        elif datemode == INVDATE_LAST_WORKDAY_CURRYEAR:
            dt1 = cls.get_invoice_date_by_createdate(INVDATE_LAST_DAY_CURRYEAR, crdate)
            return workday_backward(dt1)
        elif datemode == INVDATE_LAST_DAY_PREVYEAR:
            return date(crdate.year, 1, 1) - timedelta(days=1)
        elif datemode == INVDATE_LAST_WORKDAY_PREVYEAR:
            dt1 = cls.get_invoice_date_by_createdate(INVDATE_LAST_DAY_PREVYEAR, crdate)
            return workday_backward(dt1)
        else :
            raise ValueError(u"invalid value for the parameter 'datemode': %s" % datemode)

    @classmethod
    def get_amount(cls, invoices, names):
        """ calculate amounts
        """
        AccountTax = Pool().get('account.tax')
        erg1 = {
                'untaxed_amount': {},
                'tax_amount': {},
                'total_amount': {},
            }
        for i in invoices:
            erg1['untaxed_amount'][i.id] = _ZERO
            erg1['tax_amount'][i.id] = _ZERO
            erg1['total_amount'][i.id] = _ZERO

        for i in invoices:
            for k in i.lines:
                if not k.type == LINETYP_LINE:
                    continue
                
                # calculate taxes
                taxlist = AccountTax.compute(k.taxes, k.unit_price, Decimal(str(k.quantity)))

                for l in taxlist:
                    erg1['untaxed_amount'][i.id] += l['base']
                    break
                
                for l in taxlist:
                    erg1['tax_amount'][i.id] += l['amount']
            
            if i.invtype in ['in_invoice', 'out_credit_note']:
                erg1['untaxed_amount'][i.id] *= -1
                erg1['tax_amount'][i.id] *= -1
            erg1['total_amount'][i.id] = erg1['untaxed_amount'][i.id] + erg1['tax_amount'][i.id]

        for v1 in erg1.keys():
            if v1 not in names:
                del erg1[v1]
        return erg1

    @classmethod
    def get_date_byrule(cls, param, step=0):
        """ calculate date of next run by rule
            'item' = instance of invoicetemplate
            'step': 0 = next from today, 1 = 2nd from today, ...
        """
        if param['intervalunit'] == REPEAT_DAILY:
            unit1 = rrule.DAILY
        elif param['intervalunit'] == REPEAT_WEEKLY:
            unit1 = rrule.WEEKLY
        elif param['intervalunit'] == REPEAT_MONTHLY:
            unit1 = rrule.MONTHLY
        elif param['intervalunit'] == REPEAT_YEARLY:
            unit1 = rrule.YEARLY
        else :
            raise ValueError(u"Value 'intervalunit' invalid: %s" % param['intervalunit'])

        # workday-default: False
        wkday = False
        if 'runatweekday' in param:
            wkday = param['runatweekday']
        
        reprule = rrule.rrule(
                    cache=True,
                    dtstart=param['date_start'],
                    freq=unit1, 
                    interval=param['intervalnumber'],
                )
        
        # start from yesterday
        dt1 = date.today() - timedelta(days=1)
        
        # go through the interval steps to a step in the future
        cnt1 = 0
        while dt1 <= date.today():
            dt1 = reprule[cnt1].date()
            cnt1 += 1
        # cnt1 --> step=0
        
        # calculated execution date
        dt2 = reprule[cnt1 - 1 + step].date()
        
        if wkday == True:
            dt2 = cls.workday_forward(dt2)
            
        return dt2

    @classmethod
    def get_nextrun(cls, items, names):
        """ get next run dates
        """
        erg1 = {'nextrun': {}}
        
        # prepare result
        for i in items:
            erg1['nextrun'][i.id] = None
        
        for i in items:
            erg1['nextrun'][i.id] = cls.get_date_byrule({
                    'intervalunit': i.intervalunit,
                    'date_start': i.date_start,
                    'intervalnumber': i.intervalnumber,
                    'runatweekday': i.runatweekday,
                }, 0)
        return erg1

    @classmethod
    def format_currency(cls, value, lang, currency, symbol=True, grouping=True):
        pool = Pool()
        Lang = pool.get('ir.lang')

        return Lang.currency(lang, value, currency, symbol, grouping)

    @classmethod
    def format_date(cls, value, lang):
        pool = Pool()
        Lang = pool.get('ir.lang')
        Config = pool.get('ir.configuration')

        if lang:
            locale_format = lang.date
            code = lang.code
        else:
            locale_format = Lang.default_date()
            code = Config.get_language()
        return Lang.strftime(value, code, locale_format)

    @classmethod
    def replace_placeholder(cls, inv_item, inv_new, text):
        """ return the text with replaced placeholders
            inv_item = invoice-template object
            inv_new = new created invoice
            text = text with placeholders to replace
        """
        for m in [
                (inv_item, list_placeholder_templ),
                (inv_new, list_placeholder_invnew),
            ]:
            (obj_data, obj_placeh) = m
            
            if not isinstance(obj_data, type(None)):
                for i in obj_placeh:
                    (suchkey, key1, beschr, form1, repllst, subattr) = i
                    
                    if isinstance(subattr, type(None)):
                        obj_attr = getattr(obj_data, key1)
                    else :
                        obj_attr = getattr(getattr(obj_data, key1), subattr)
    
                    if isinstance(obj_attr, type(None)):
                        neutext = ''
                    elif isinstance(obj_attr, type(date.today())):
                        neutext = cls.format_date(obj_attr, inv_item.party.lang)
                    elif suchkey in ['untaxed', 'tax', 'total']:
                        neutext = cls.format_currency(obj_attr, inv_item.party.lang, inv_item.currency)
                    else :
                        neutext = form1 % obj_attr
    
                    for k in repllst:
                        (von, nach) = k
                        neutext = neutxt.replace(von, nach)
                    text = text.replace(u'[%s]' % suchkey, neutext)
        return text

    @classmethod
    def create(cls, vlist):
        """ create item
        """
        vlist = [x.copy() for x in vlist]
        for values in vlist:
            values['active'] = True
            if values['active2'] == True:
                values['date_nextrun'] = cls.get_date_byrule(values, 0)
        return super(InvoiceTemplate, cls).create(vlist)

    @classmethod
    def write(cls, *args):
        """ reset 'calls_done' if activated
        """
        actions = iter(args)
        for invtempl, values in zip(actions, actions):
            if 'calls_to_go' in values:
                values['calls_done'] = 0
            if 'active2' in values:
                if values['active2'] == True:
                    values['calls_done'] = 0
            
            # recalc next run
            if ('intervalunit' in values) or \
                ('date_start' in values) or \
                ('intervalnumber' in values) or \
                ('runatweekday' in values) or \
                ('active2' in values):
                
                if len(invtempl) != 1:
                    raise ValueError(u'number of item not 1')

                r1 = {}
                for k in ['intervalunit', 'date_start', 'intervalnumber', 'runatweekday']:
                    r1[k] = getattr(invtempl[0], k)
                    if k in values:
                        r1[k] = values[k]

                if 'active2' in values.keys():
                    if values['active2'] == True:
                        values['date_nextrun'] = cls.get_date_byrule(r1, 0)
                    else :
                        values['date_nextrun'] = None
                else :
                    values['date_nextrun'] = cls.get_date_byrule(r1, 0)

        super(InvoiceTemplate, cls).write(*args)

# end InvoiceTemplate


class InvoiceLine(ModelSQL, ModelView):
    """ Invoice Line
    """
    __name__ = 'periodic_invoice.invline'

    invoice = fields.Many2One(model_name='periodic_invoice.invoice', string=u'Invoice', 
                ondelete='CASCADE', select=True, required=True)
    sequence = fields.Integer(string=u'Sequence', select=True)
    type = fields.Selection(selection=sel_invline_type, string=u'Type', 
                select=True, required=True)
    unit_digits = fields.Function(fields.Integer(string=u'Unit Digits'), 'on_change_with_unit_digits')
    inv_company = fields.Function(fields.Many2One(model_name='company.company', 
                string=u'Company'), 'on_change_with_inv_company')
    inv_party = fields.Function(fields.Many2One(model_name='party.party', 
                string=u'Party'), 'on_change_with_party')
    inv_type = fields.Function(fields.Selection(selection=INV_TYPES, string=u'Type'),
                'on_change_with_inv_type')
    product_uom_category = fields.Function(fields.Many2One(model_name='product.uom.category', 
                string=u'Product Uom Category'), 'on_change_with_product_uom_category')
    product = fields.Many2One(model_name='product.product', string=u'Product',
                states={
                    'invisible': Eval('type') != LINETYP_LINE,
                }, depends=['type'])
    quantity = fields.Float(string=u'Quantity', digits=(16, Eval('unit_digits', 2)),
                states={
                    'invisible': Eval('type') != LINETYP_LINE,
                    'required': Eval('type') == LINETYP_LINE,
                }, depends=['type', 'unit_digits'])
    unit = fields.Many2One(model_name=u'product.uom', string=u'Unit',
                states={
                    'required': Bool(Eval('product')),
                    'invisible': Eval('type') != LINETYP_LINE,
                },
                domain=[
                    If(Bool(Eval('product_uom_category')),
                        ('category', '=', Eval('product_uom_category')),
                        ('category', '!=', -1)),
                ], depends=['product', 'type', 'product_uom_category'])
    description = fields.Text('Description', size=None, required=True)
    note = fields.Text('Note')
    account = fields.Many2One(model_name='account.account', string=u'Account',
                states={
                    'invisible': Eval('type') != LINETYP_LINE,
                    'required': Eval('type') == LINETYP_LINE,
                }, depends=['type'])
    unit_price = fields.Numeric(string=u'Unit Price', digits=price_digits,
                states={
                    'invisible': Eval('type') != LINETYP_LINE,
                    'required': Eval('type') == LINETYP_LINE,
                }, depends=['type'])
    amount = fields.Function(fields.Numeric(string=u'Amount',
                digits=(16, Eval('_parent_invoice', {}).get('currency_digits', Eval('currency_digits', 2))),
                states={
                    'invisible': ~Eval('type').in_([LINETYP_LINE, LINETYP_SUBTOTAL]),
                    }, depends=['type', 'currency_digits']), 'get_amount')
    taxes = fields.Many2Many('periodic_invoice.linetax', origin='line', target='tax', 
                string=u'Taxes',
                order=[('tax.sequence', 'ASC'), ('tax.id', 'ASC')],
                domain=[('parent', '=', None), 
                        ['OR',
                            ('group', '=', None),
                            ('group.kind', 'in',
                                If(Bool(Eval('_parent_invoice')),
                                    If(Eval('_parent_invoice', {}).get('invtype').in_(['out_invoice', 'out_credit_note']),
                                        ['sale', 'both'],
                                        ['purchase', 'both']
                                    ),
                                    If(Eval('inv_type').in_(['out_invoice', 'out_credit_note']),
                                        ['sale', 'both'],
                                        ['purchase', 'both']
                                    )
                                )
                            )
                        ],
                        ('company', '=', Eval('inv_company', -1)),
                ],
                states={
                    'invisible': Eval('type') != 'line',
                }, depends=['type', 'inv_type', 'inv_company'])

    @classmethod
    def __setup__(cls):
        super(InvoiceLine, cls).__setup__()
        tab_invl = cls.__table__()
        cls._sql_constraints += [
            ('type_account',
            Check(tab_invl, 
                    ((tab_invl.type == LINETYP_LINE) & (tab_invl.account != Null)) | 
                    (tab_invl.type != LINETYP_LINE)
                ),
            u"Line with 'line' type must have an account."),
            ('type_invoice',
            Check(tab_invl, 
                    ((tab_invl.type != LINETYP_LINE) & (tab_invl.invoice != Null)) | 
                    (tab_invl.type == LINETYP_LINE)
                ),
            u"Line without 'line' type must have an invoice."),
            ]
        cls._order.insert(0, ('sequence', 'ASC'))

        # account domain
        cls.account.domain = [
            ('company', '=', Eval('inv_company', -1)),
            If(Bool(Eval('_parent_invoice')),
                If(Eval('_parent_invoice', {}).get('invtype').in_(['out_invoice', 'out_credit_note']),
                    ('kind', 'in', cls._account_domain('out')),
                    If(Eval('_parent_invoice', {}).get('invtype').in_(['in_invoice', 'in_credit_note']),
                        ('kind', 'in', cls._account_domain('in')),
                        ('kind', 'in', cls._account_domain('out') + cls._account_domain('in'))
                    )
                ),
                If(Eval('inv_type').in_(['out_invoice', 'out_credit_note']),
                    ('kind', 'in', cls._account_domain('out')),
                    If(Eval('inv_type').in_(['in_invoice', 'in_credit_note']),
                        ('kind', 'in', cls._account_domain('in')),
                        ('kind', 'in', cls._account_domain('out') + cls._account_domain('in')))
                )
            ),
            ]
        cls.account.depends += ['inv_company', 'invoice_type']

    @staticmethod
    def _account_domain(type_):
        if type_ == 'out':
            return ['revenue']
        elif type_ == 'in':
            return ['expense']

    @fields.depends('invoice')
    def on_change_with_inv_type(self, name=None):
        if self.invoice:
            return self.invoice.invtype

    @fields.depends('invoice')
    def on_change_with_party(self, name=None):
        if self.invoice:
            return self.invoice.party.id

    @fields.depends('invoice')
    def on_change_with_inv_company(self, name=None):
        if self.invoice:
            return self.invoice.company.id
        
    @fields.depends('product')
    def on_change_with_product_uom_category(self, name=None):
        if self.product:
            return self.product.default_uom_category.id

    @fields.depends('unit')
    def on_change_with_unit_digits(self, name=None):
        if self.unit:
            return self.unit.digits
        return 2

    def _get_tax_rule_pattern(self):
        """ Get tax rule pattern
        """
        return {}

    @fields.depends('product', 'unit', 'invoice', 'description', 'account', 'inv_party', 'taxes')
    def on_change_product(self):
        """ on-change: product
        """
        pool = Pool()
        Product = pool.get('product.product')

        context = {}
        if not self.product:
            return

        party = None
        if self.invoice and self.invoice.party:
            party = self.invoice.party
        elif self.inv_party:
            party = self.inv_party

        if self.invoice and self.invoice.invtype:
            type_ = self.invoice.invtype
        else:
            type_ = '-'
        if type_ in ['in_invoice', 'in_credit_note']:
            try:
                self.account = self.product.account_expense_used
            except Exception:
                pass

            taxes = []
            pattern = self._get_tax_rule_pattern()
            for tax in self.product.supplier_taxes_used:
                if party and party.supplier_tax_rule:
                    tax_ids = party.supplier_tax_rule.apply(tax, pattern)
                    if tax_ids:
                        taxes.extend(tax_ids)
                    continue
                taxes.append(tax)
            if party and party.supplier_tax_rule:
                tax_ids = party.supplier_tax_rule.apply(None, pattern)
                if tax_ids:
                    taxes.extend(tax_ids)
            self.taxes = taxes
        elif type_ in ['out_credit_note', 'out_invoice']:
            try:
                self.account = self.product.account_revenue_used
            except Exception:
                pass
            taxes = []
            pattern = self._get_tax_rule_pattern()
            for tax in self.product.customer_taxes_used:
                if party and party.customer_tax_rule:
                    tax_ids = party.customer_tax_rule.apply(tax, pattern)
                    if tax_ids:
                        taxes.extend(tax_ids)
                    continue
                taxes.append(tax.id)
            if party and party.customer_tax_rule:
                tax_ids = party.customer_tax_rule.apply(None, pattern)
                if tax_ids:
                    taxes.extend(tax_ids)
            self.taxes = taxes

        if not self.description:
            with Transaction().set_context(**context):
                self.description = Product(self.product.id).rec_name

        category = self.product.default_uom.category
        if not self.unit or self.unit not in category.uoms:
            self.unit = self.product.default_uom.id
            self.unit_digits = self.product.default_uom.digits

    @fields.depends('type', 'quantity', 'unit_price', '_parent_invoice.currency', 'currency')
    def on_change_with_amount(self):
        if self.type == LINETYP_LINE:
            currency = (self.invoice.currency or None)
            amount = Decimal(str(self.quantity or '0.0')) * (self.unit_price or _ZERO)
            if currency:
                return currency.round(amount)
            return amount
        return _ZERO

    def get_amount(self, name):
        """ calculate: amount 
        """
        if self.type == LINETYP_LINE:
            return self.on_change_with_amount()
        elif self.type == LINETYP_SUBTOTAL:
            subtotal = _ZERO
            for line2 in self.invoice.lines:
                if line2.type == LINETYP_LINE:
                    subtotal += line2.invoice.currency.round(
                        Decimal(str(line2.quantity)) * line2.unit_price)
                elif line2.type == LINETYP_SUBTOTAL:
                    if self == line2:
                        break
                    subtotal = _ZERO
            return subtotal
        else:
            return _ZERO

    @staticmethod
    def order_sequence(tables):
        """ sort by sequence
        """
        table, _ = tables[None]
        return [Case((table.sequence == Null, 0), else_=1), table.sequence]

    @staticmethod
    def default_type():
        """ default: type
        """
        return LINETYP_LINE

# end InvoiceLine


class InvoiceLineTax(ModelSQL):
    'invoice-line-tax'
    __name__ = 'periodic_invoice.linetax'

    line = fields.Many2One(model_name='periodic_invoice.invline', string=u'Invoice Line',
                ondelete='CASCADE', select=True, required=True)
    tax = fields.Many2One(model_name='account.tax', string=u'Tax', ondelete='RESTRICT', required=True)
    
# end InvoiceLineTax


class InvoicesRel(ModelSQL):
    'template-invoice-rel'
    __name__ = 'periodic_invoice.invoices_rel'
    
    invtempl = fields.Many2One(model_name='periodic_invoice.invoice', 
                string=u'Invoice template', ondelete='CASCADE', required=True, select=True)
    invoice = fields.Many2One(model_name='account.invoice', 
                string=u'Invoice', ondelete='CASCADE', required=True, select=True)

    @classmethod
    def __setup__(cls):
        super(InvoicesRel, cls).__setup__()
        tab_rel = cls.__table__()
        cls._sql_constraints.extend([
            ('invoice_uniqu', 
            Unique(tab_rel, tab_rel.invoice, tab_rel.invtempl), 
            u'This invoice is already linked.'),
            ])

# end InvoicesRel

