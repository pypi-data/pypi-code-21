# -*- coding: utf-8 -*-

from trytond.pool import Pool
from .account import AccountInvLine

def register():
    Pool.register(
        AccountInvLine,
        module='account_pos_soldproducts', type_='model')
