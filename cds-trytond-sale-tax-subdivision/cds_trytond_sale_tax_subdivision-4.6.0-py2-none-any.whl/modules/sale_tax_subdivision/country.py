# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import Pool
from trytond.pyson import Eval

__all__ = ['Subdivision']


class Subdivision(ModelSQL, ModelView):
    """Subdivision
    This feature sets sale taxes according to subdivision of invoice address.

    The customer_tax_rule field is added here to specify what rule to set for
    what subdivision when calculating taxes on a sale.
    """
    __name__ = 'country.subdivision'

    customer_tax_rule = fields.Many2One(
        'account.tax.rule',
        'Customer Tax Rule',
        help='Apply this tax rule to customer sales from this subdivision.'
    )

