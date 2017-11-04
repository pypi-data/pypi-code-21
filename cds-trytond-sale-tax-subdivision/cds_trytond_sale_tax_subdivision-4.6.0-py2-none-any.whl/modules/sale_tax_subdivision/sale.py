# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import Pool
from trytond.pyson import Eval

from trytond.modules.account.tax import TaxableMixin

__all__ = ['Sale']


class Sale(ModelSQL, ModelView, TaxableMixin):
    """Sale
    This feature sets sale taxes according to subdivision of invoice_address

    Methods are added here to update the invoice party's customer tax rule and
    
    """
    __name__ = 'sale.sale'

    def total_taxes(self):
        TaxCode = Pool().get('account.tax.code')
        taxes = self._get_taxes()
        for tax in taxes.itervalues():
            tax['sale'] = self.id
            if tax['tax_code']:
                tax['tax_code_code'] = TaxCode(tax['tax_code']).code
        return taxes

    def calculate(self):
        '''
        Calculate (or re-calculate) prices and taxes on entire sale
        NOTE: This might be better put into a module of its own in the future
        such as a "sale_cart" if it simplifies the creation of the flask app
        '''
        for line in self.lines:
            line.calculate()


class SaleLine(ModelSQL, ModelView):
    "Sale line"
    __name__ = 'sale.line'

    def calculate(self):
        '''
        Calculate (or re-calculate) prices and taxes on a line item
        NOTE: This might be better put into a module of its own in the future
        such as a "sale_cart" if it simplifies the creation of the flask app
        '''
        pool = Pool()
        SaleLine = pool.get('sale.line')
        retvals = SaleLine(self.id).on_change_product()
   
        if 'taxes' in retvals:
            self.taxes = retvals.taxes
            self.save()

    @fields.depends('product', 'unit', 'quantity', 'description',
        '_parent_sale.party', '_parent_sale.currency',
        '_parent_sale.sale_date', '_parent_sale.invoice_address')
    def on_change_product(self):
        super(SaleLine, self).on_change_product()
        subdiv_taxes = []
        if self.sale.invoice_address:
            subdiv = self.sale.invoice_address.subdivision
        else:
            subdiv = None
        if subdiv:
            tax_rule = subdiv.customer_tax_rule
        else:
            tax_rule = None

        if tax_rule:
            pattern = self._get_tax_rule_pattern()
            for tax in self.taxes:
                tax_ids = tax_rule.apply(tax, pattern)
                if tax_ids:
                     subdiv_taxes.extend(tax_ids)
                     continue
                # TODO: option to disable below to default to no taxes
                # subdiv_taxes.append(tax.id)
                pass

        self.taxes = subdiv_taxes
