# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify it
#     under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import SUPERUSER_ID
from openerp.osv import fields, orm
from openerp.tools.translate import _

TIN_LENGTH = 10
VAT_LENGTH = 10


class res_partner(orm.Model):

    _inherit = 'res.partner'

    _columns = {
        'vat': fields.char('TIN', size=TIN_LENGTH,
                           help="Tax Identification Number. Check the box if "
                                "this contact is subjected to taxes. Used by "
                                "the some of the legal statements."),
        'vat_number': fields.char('VAT', size=VAT_LENGTH, select=True,
                                  help="VAT Registration Number"),
    }

    def _check_vat_common(self, cr, uid, _id, field_name, field_value,
                          field_length, context=None):

        # If the field isn't set let it pass
        if not field_value:
            return True

        # Make sure the field is:
        #   1. 10 digits long
        #   2. Numeric
        #   3. Unique
        #
        if len(field_value) != field_length:
            return False
        elif not str(field_value).isdigit():
            return False

        return True

    def check_tin(self, cr, uid, ids, context=None):

        res = True
        for partner in self.browse(cr, uid, ids, context=context):
            res = self._check_vat_common(cr, uid, partner.id, 'vat',
                                         partner.vat, TIN_LENGTH,
                                         context=context)

        return res

    def check_vat(self, cr, uid, ids, context=None):

        res = True
        for partner in self.browse(cr, uid, ids, context=context):
            res = self._check_vat_common(cr, uid, partner.id, 'vat_number',
                                         partner.vat_number, VAT_LENGTH,
                                         context=context)

        return res

    def _check_unique_common(self, cr, uid, _id, field_name, field_value,
                             context=None):

        # If the field isn't set let it pass
        if not field_value:
            return True

        duplicate_ids = self.search(cr, SUPERUSER_ID,
                                    [(field_name, '=', field_value),
                                     ('id', '!=', _id)], context=context)
        if len(duplicate_ids) > 0:
            return False

        return True

    def check_tin_unique(self, cr, uid, ids, context=None):

        res = True
        for partner in self.browse(cr, uid, ids, context=context):
            res = self._check_unique_common(cr, uid, partner.id, 'vat',
                                            partner.vat, context=context)

        return res

    def check_vat_unique(self, cr, uid, ids, context=None):

        res = True
        for partner in self.browse(cr, uid, ids, context=context):
            res = self._check_unique_common(cr, uid, partner.id, 'vat_number',
                                            partner.vat_number,
                                            context=context)

        return res

    _constraints = [(check_vat,
                     _("VAT registration number is invalid"), ["vat_number"]),
                    (check_vat_unique,
                     _("VAT registration number in use by another partner!"),
                     ["vat_number"]),
                    (check_tin,
                     _("Taxpayer ID Number (TIN) is invalid"), ["vat"]),
                    (check_tin_unique,
                     _("Taxpayer ID Number (TIN) in use by another partner!"),
                     ["vat"])]


class res_company(orm.Model):

    _inherit = 'res.company'

    def write(self, cr, uid, ids, vals, context=None):
        """When the TIN and VAT registration numbers are changed in the,
        company, change them on the partner as well"""

        res = super(res_company, self).write(cr, uid, ids, vals,
                                             context=context)

        write_res = {}
        partner_obj = self.pool['res.partner']
        if 'vat' in list(vals.keys()):
            write_res.update({'vat': vals['vat'],
                              'vat_subjected': bool(vals.get('vat'))})
        if 'vat_number' in list(vals.keys()):
            write_res.update({'vat_number': vals['vat_number']})

        if 'vat' in list(write_res.keys()) or \
                'vat_number' in list(write_res.keys()):
            for company in self.browse(cr, uid, ids, context=context):
                partner_obj.write(cr, uid, company.partner_id.id, write_res,
                                  context=context)

        return res
