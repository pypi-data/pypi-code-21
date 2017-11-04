# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from . import country
from . import sale


def register():
    Pool.register(
        country.Subdivision,
        sale.Sale,
        sale.SaleLine,
        module='sale_tax_subdivision', type_='model')
