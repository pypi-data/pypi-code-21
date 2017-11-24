# -*- coding: utf-8 -*-

from decimal import Decimal
from trytond.model import fields
from trytond.pyson import Eval
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from sql.functions import Round, DateTrunc, CurrentDate, Age
from sql.conditionals import Case
from sql.aggregate import Sum
from sqlextension import StringAgg

__all__ = []
__metaclass__ = PoolMeta


class AccountInvLine:
    __name__ = 'account.invoice.line'
    
    sa_invoicedate = fields.Function(fields.Date(string=u'Invoice Date', readonly=True), 
            'get_linedata', searcher='search_sa_invoicedate')
    sa_priceunitnet = fields.Function(fields.Numeric(string=u'Unit price net', readonly=True, digits=(16, 2)), 
            'get_linedata', searcher='search_sa_priceunitnet')
    sa_priceunitgross = fields.Function(fields.Numeric(string=u'Unit price gross', readonly=True, digits=(16, 2)), 
            'get_linedata', searcher='search_sa_priceunitgross')
    sa_pricenet = fields.Function(fields.Numeric(string=u'Net price', readonly=True, digits=(16, 2)), 
            'get_linedata', searcher='search_sa_pricenet')
    sa_pricegross = fields.Function(fields.Numeric(string=u'Gross price', readonly=True, digits=(16, 2)), 
            'get_linedata', searcher='search_sa_pricegross')
    sa_taxes = fields.Function(fields.Numeric(string=u'Taxes', readonly=True, digits=(16, 2)), 
            'get_linedata', searcher='search_sa_taxes')
    sa_taxnames = fields.Function(fields.Char(string=u'Taxnames', readonly=True), 'get_linedata')
    sa_currency = fields.Function(fields.Char(string=u'Currency', readonly=True), 
            'get_linedata', searcher='search_sa_currency')
    sa_currency2 = fields.Function(fields.Many2One(string=u'Currency', 
            model_name='currency.currency', readonly=True), 'get_linedata')
    sa_invnr = fields.Function(fields.Char(string=u'Invoice No.', readonly=True), 
            'get_linedata', searcher='search_sa_invnr')
    sa_invoice = fields.Function(fields.Many2One(string=u'Invoice', readonly=True,
            model_name=u'account.invoice'), 'get_linedata')
    sa_account = fields.Function(fields.Char(string=u'Account', readonly=True), 
            'get_linedata', searcher='search_sa_account')
    sa_accdate = fields.Function(fields.Date(string=u'Accounting Date', readonly=True), 'get_linedata')
    sa_invstate = fields.Function(fields.Char(string=u'State', readonly=True), 
            'get_linedata', searcher='search_sa_invstate')
    sa_partyname = fields.Function(fields.Char(string=u'Party', readonly=True), 
            'get_linedata', searcher='search_sa_partyname')
    sa_party = fields.Function(fields.Many2One(string=u'Party', 
            model_name=u'party.party', readonly=True), 'get_linedata')
    sa_invtype = fields.Function(fields.Char(string=u'Invoice Type', readonly=True), 
            'get_linedata', searcher='search_sa_invtype')
    sa_prodname = fields.Function(fields.Char(string=u'Product', readonly=True), 
            'get_linedata', searcher='search_sa_prodname')
    sa_quantity = fields.Function(fields.Numeric(string=u'Quantity', readonly=True, digits=(16, 2)), 
            'get_linedata', searcher='search_sa_quantity')
    sa_currweek = fields.Function(fields.Boolean(string=u'Current week', readonly=True), 
            'get_linedata', searcher='search_sa_currweek')
    sa_agedays = fields.Function(fields.Boolean(string=u'Age days', readonly=True), 
            'get_linedata', searcher='search_sa_agedays')

    @classmethod
    def __setup__(cls):
        super(AccountInvLine, cls).__setup__()
        cls._order.insert(0, ('sa_invoicedate', 'DESC'))

    @staticmethod
    def order_sa_invoicedate(tables):
        tab_invline, _ = tables[None]
        return [tab_invline.create_date]

    @staticmethod
    def order_sa_prodname(tables):
        tab_invline, _ = tables[None]
        return [tab_invline.description]

    @staticmethod
    def order_sa_quantity(tables):
        tab_invline, _ = tables[None]
        return [tab_invline.quantity]

    @staticmethod
    def order_sa_priceunitnet(tables):
        tab_invline, _ = tables[None]
        return [tab_invline.unit_price]

    @classmethod
    def search_sa_invoicedate(cls, name, clause):
        """ sql-code to search in invoice-date
        """
        Operator = fields.SQL_OPERATORS[clause[1]]
        
        tab_sql = cls.get_sql_table()
        
        qu1 = tab_sql.select(tab_sql.id_line,
                    where=Operator(tab_sql.invoice_date, clause[2])
                )
        return [('id', 'in', qu1)]
        
    @classmethod
    def search_sa_priceunitnet(cls, name, clause):
        """ sql-code to search in unitprice-net
        """
        Operator = fields.SQL_OPERATORS[clause[1]]
        
        tab_sql = cls.get_sql_table()
        
        qu1 = tab_sql.select(tab_sql.id_line,
                    where=Operator(tab_sql.priceunitnet, clause[2])
                )
        return [('id', 'in', qu1)]

    @classmethod
    def search_sa_priceunitgross(cls, name, clause):
        """ sql-code to search in unitprice with taxes
        """
        Operator = fields.SQL_OPERATORS[clause[1]]
        
        tab_sql = cls.get_sql_table()
        
        qu1 = tab_sql.select(tab_sql.id_line,
                    where=Operator(tab_sql.priceunitgross, clause[2])
                )
        return [('id', 'in', qu1)]

    @classmethod
    def search_sa_pricenet(cls, name, clause):
        """ sql-code to search in price-net
        """
        Operator = fields.SQL_OPERATORS[clause[1]]
        
        tab_sql = cls.get_sql_table()
        
        qu1 = tab_sql.select(tab_sql.id_line,
                    where=Operator(tab_sql.pricenet, clause[2])
                )
        return [('id', 'in', qu1)]

    @classmethod
    def search_sa_pricegross(cls, name, clause):
        """ sql-code to search in price with taxes
        """
        Operator = fields.SQL_OPERATORS[clause[1]]
        
        tab_sql = cls.get_sql_table()
        
        qu1 = tab_sql.select(tab_sql.id_line,
                    where=Operator(tab_sql.pricegross, clause[2])
                )
        return [('id', 'in', qu1)]

    @classmethod
    def search_sa_taxes(cls, name, clause):
        """ sql-code to search in taxes
        """
        Operator = fields.SQL_OPERATORS[clause[1]]
        
        tab_sql = cls.get_sql_table()
        
        qu1 = tab_sql.select(tab_sql.id_line,
                    where=Operator(tab_sql.taxsum, clause[2])
                )
        return [('id', 'in', qu1)]

    @classmethod
    def search_sa_currency(cls, name, clause):
        """ sql-code to search in currency
        """
        Operator = fields.SQL_OPERATORS[clause[1]]
        
        tab_sql = cls.get_sql_table()
        
        qu1 = tab_sql.select(tab_sql.id_line,
                    where=Operator(tab_sql.currcode, clause[2])
                )
        return [('id', 'in', qu1)]

    @classmethod
    def search_sa_invnr(cls, name, clause):
        """ sql-code to search in invoice-no
        """
        Operator = fields.SQL_OPERATORS[clause[1]]
        
        tab_sql = cls.get_sql_table()
        
        qu1 = tab_sql.select(tab_sql.id_line,
                    where=Operator(tab_sql.invnr, clause[2])
                )
        return [('id', 'in', qu1)]

    @classmethod
    def search_sa_account(cls, name, clause):
        """ sql-code to search in account
        """
        Operator = fields.SQL_OPERATORS[clause[1]]
        
        tab_sql = cls.get_sql_table()
        
        qu1 = tab_sql.select(tab_sql.id_line,
                    where=Operator(tab_sql.account, clause[2])
                )
        return [('id', 'in', qu1)]

    @classmethod
    def search_sa_invstate(cls, name, clause):
        """ sql-code to search in invoice-state
        """
        Operator = fields.SQL_OPERATORS[clause[1]]
        
        tab_sql = cls.get_sql_table()
        
        qu1 = tab_sql.select(tab_sql.id_line,
                    where=Operator(tab_sql.invstate, clause[2])
                )
        return [('id', 'in', qu1)]

    @classmethod
    def search_sa_partyname(cls, name, clause):
        """ sql-code to search in party
        """
        Operator = fields.SQL_OPERATORS[clause[1]]
        
        tab_sql = cls.get_sql_table()
        
        qu1 = tab_sql.select(tab_sql.id_line,
                    where=Operator(tab_sql.partyname, clause[2])
                )
        return [('id', 'in', qu1)]

    @classmethod
    def search_sa_invtype(cls, name, clause):
        """ sql-code to search in invoice-type
        """
        Operator = fields.SQL_OPERATORS[clause[1]]
        
        tab_sql = cls.get_sql_table()
        
        qu1 = tab_sql.select(tab_sql.id_line,
                    where=Operator(tab_sql.invtype, clause[2])
                )
        return [('id', 'in', qu1)]

    @classmethod
    def search_sa_prodname(cls, name, clause):
        """ sql-code to search in product
        """
        Operator = fields.SQL_OPERATORS[clause[1]]
        
        tab_sql = cls.get_sql_table()
        
        qu1 = tab_sql.select(tab_sql.id_line,
                    where=Operator(tab_sql.prodname, clause[2])
                )
        return [('id', 'in', qu1)]

    @classmethod
    def search_sa_quantity(cls, name, clause):
        """ sql-code to search in quanity
        """
        Operator = fields.SQL_OPERATORS[clause[1]]
        
        tab_sql = cls.get_sql_table()
        
        qu1 = tab_sql.select(tab_sql.id_line,
                    where=Operator(tab_sql.quantity, clause[2])
                )
        return [('id', 'in', qu1)]

    @classmethod
    def search_sa_currweek(cls, name, clause):
        """ sql-code to search in quanity
        """
        Operator = fields.SQL_OPERATORS[clause[1]]
        
        tab_sql = cls.get_sql_table()
        
        qu1 = tab_sql.select(tab_sql.id_line,
                    where=Operator(tab_sql.currweek, clause[2])
                )
        return [('id', 'in', qu1)]

    @classmethod
    def search_sa_agedays(cls, name, clause):
        """ sql-code to search in quanity
        """
        Operator = fields.SQL_OPERATORS[clause[1]]
        
        tab_sql = cls.get_sql_table()
        
        qu1 = tab_sql.select(tab_sql.id_line,
                    where=Operator(tab_sql.agedays, clause[2])
                )
        return [('id', 'in', qu1)]

    @classmethod
    def get_sql_table(cls):
        """ create sql-view
        """
        pool = Pool()
        cursor = Transaction().cursor
        AccountInvoice = pool.get('account.invoice')
        AccountInvoiceLine = pool.get('account.invoice.line')
        AccInvLineTax = pool.get('account.invoice.line-account.tax')
        AccountTax = pool.get('account.tax')
        Account = pool.get('account.account')
        Currency = pool.get('currency.currency')
        Party = pool.get('party.party')
        
        tab_accinv = AccountInvoice.__table__()
        tab_accinvline = AccountInvoiceLine.__table__()
        tab_accinvlintax = AccInvLineTax.__table__()
        tab_acctax = AccountTax.__table__()
        tab_acc = Account.__table__()
        tab_curr = Currency.__table__()
        tab_party = Party.__table__()
         
        qu1 = tab_accinv.join(tab_accinvline, condition=tab_accinvline.invoice==tab_accinv.id
                ).join(tab_accinvlintax, condition=tab_accinvlintax.line==tab_accinvline.id
                ).join(tab_acctax, condition=tab_accinvlintax.tax==tab_acctax.id
                ).join(tab_curr, condition=tab_curr.id==tab_accinv.currency
                ).join(tab_acc, condition=tab_acc.id==tab_accinvline.account
                ).join(tab_party, condition=tab_party.id==tab_accinv.party
                ).select(tab_accinvline.id.as_('id_line'),
                    tab_accinv.invoice_date,
                    tab_accinvline.quantity,
                    Round(tab_accinvline.unit_price, 2).as_('priceunitnet'),
                    Round((Sum(tab_acctax.rate * tab_accinvline.unit_price) + 
                            tab_accinvline.unit_price), 2).as_('priceunitgross'),
                    Round(tab_accinvline.unit_price * tab_accinvline.quantity.cast('numeric'), 2).as_('pricenet'),
                    Round((Sum(tab_acctax.rate * tab_accinvline.unit_price) + 
                            tab_accinvline.unit_price) * tab_accinvline.quantity.cast('numeric'), 2).as_('pricegross'),
                    Round(Sum(tab_acctax.rate * tab_accinvline.unit_price) * 
                            tab_accinvline.quantity.cast('numeric'), 2).as_('taxsum'),
                    StringAgg(tab_acctax.name, u', ').as_('taxnames'),
                    tab_curr.code.as_('currcode'),
                    tab_curr.id.as_('currid'),
                    tab_accinv.number.as_('invnr'),
                    tab_accinv.id.as_('invid'),
                    tab_acc.code.as_('account'),
                    tab_accinv.accounting_date.as_('accdate'),
                    tab_accinv.state.as_('invstate'),
                    tab_party.name.as_('partyname'),
                    tab_party.id.as_('partyid'),
                    tab_accinv.type.as_('invtype'),
                    tab_accinvline.description.as_('prodname'),
                    Case(
                        (DateTrunc('week', CurrentDate()) == DateTrunc('week', tab_accinv.invoice_date), True),
                        else_ = False
                    ).as_('currweek'),
                    (CurrentDate() - tab_accinv.invoice_date).cast('integer').as_('agedays'),
                    group_by=[tab_accinvline.id, tab_accinv.invoice_date, tab_curr.code, tab_accinv.number,
                            tab_acc.code, tab_accinv.accounting_date, tab_accinv.state, tab_party.name,
                            tab_accinv.type, tab_curr.id, tab_party.id, tab_accinv.id
                        ]
                )
        return qu1
        
    @classmethod
    def get_linedata(cls, movelines, names):
        """ collect data
        """
        cursor = Transaction().cursor
        
        erg1 = {'sa_invoicedate': {}, 'sa_prodname': {},
                'sa_priceunitnet': {}, 'sa_priceunitgross': {},
                'sa_pricenet': {}, 'sa_pricegross': {},
                'sa_taxes': {}, 'sa_taxnames': {},
                'sa_currency': {}, 'sa_currency2': {},
                'sa_invnr': {}, 'sa_invoice':{}, 'sa_invtype': {},
                'sa_account': {}, 'sa_accdate': {},
                'sa_invstate': {}, 'sa_partyname': {}, 'sa_party': {}, 
                'sa_quantity': {}, 'sa_currweek': {}, 'sa_last14day':{},
            }
        
        tab_sql = cls.get_sql_table()
        qu1 = tab_sql.select(where=tab_sql.id_line.in_([x.id for x in movelines]))

        cursor.execute(*qu1)
        l1 = cursor.fetchall()
        
        for i in l1:
            (id_line, inv_date, quantity, priceunitnet, priceunitgross, 
                pricenet, pricegross, taxsum, taxnames, currcode, currid,
                invnr, invid, account, accdate, invstate, partyname, partyid, 
                invtype, prodname, currweek, last14day) = i

            erg1['sa_invoicedate'][id_line] = inv_date
            erg1['sa_priceunitnet'][id_line] = priceunitnet
            erg1['sa_priceunitgross'][id_line] = priceunitgross
            erg1['sa_pricenet'][id_line] = pricenet
            erg1['sa_pricegross'][id_line] = pricegross
            erg1['sa_taxes'][id_line] = taxsum
            erg1['sa_taxnames'][id_line] = taxnames
            erg1['sa_currency'][id_line] = currcode
            erg1['sa_currency2'][id_line] = currid
            erg1['sa_invnr'][id_line] = invnr
            erg1['sa_account'][id_line] = account
            erg1['sa_accdate'][id_line] = accdate
            erg1['sa_invstate'][id_line] = invstate
            erg1['sa_partyname'][id_line] = partyname
            erg1['sa_party'][id_line] = partyid
            erg1['sa_invtype'][id_line] = invtype
            erg1['sa_invoice'][id_line] = invid
            erg1['sa_prodname'][id_line] = prodname
            erg1['sa_quantity'][id_line] = Decimal(quantity).quantize(Decimal('0.01'))
            erg1['sa_currweek'][id_line] = currweek
            erg1['sa_last14day'][id_line] = last14day
            
        for i in erg1.keys():
            if not i in names:
                del erg1[i]
        
        return erg1
        
# ende AccountInvLine
