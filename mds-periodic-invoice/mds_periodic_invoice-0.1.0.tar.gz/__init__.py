# -*- coding: utf-8 -*-

from trytond.pool import Pool
from .invoicetempl import InvoiceTemplate, InvoicesRel, InvoiceLine, InvoiceLineTax
from .configuration import Configuration


def register():
    Pool.register(
        Configuration,
        InvoiceTemplate,
        InvoicesRel,
        InvoiceLine,
        InvoiceLineTax,
        module='periodic_invoice', type_='model')
