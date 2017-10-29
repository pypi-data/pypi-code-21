# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Clear ICT Solutions <info@clearict.com>.
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify it
#    under the terms of the GNU Affero General Public License as published by
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

from openerp.osv import fields, orm


class res_partner(orm.Model):

    _inherit = 'res.partner'

    _columns = {
        'ethiopic_name': fields.char('Ethiopic Name', size=1024, select=True),
        'subcity': fields.char('Subcity (Woreda)', size=256, select=True),
        'kebele': fields.char('Kebele', size=8, select=True),
        'houseno': fields.char('House No', size=16, select=True),
        'et_subcity': fields.char(
            'Amharic Subcity (Woreda)', size=256, select=True),
        'et_city': fields.char('Amharic City', size=256, select=True),
        'pobox': fields.char('P.O. Box', size=16),
    }


class res_company(orm.Model):

    _inherit = 'res.company'

    _columns = {
        # Re-define from openerp/addons/base/res/res_company.py to limit size
        'vat': fields.related(
            'partner_id', 'vat', string="Tax Identification Number",
            type="char", size=10),

        'vat_number': fields.char(
            'VAT', size=10, select=True, help="VAT Registration Number"),
        'ethiopic_name': fields.related(
            'partner_id', 'ethiopic_name', string='Ethiopic Name',
            size=1024, store=True, type='char'),
    }


class res_country_state(orm.Model):

    _inherit = 'res.country.state'

    _columns = {
        'ethiopic_name': fields.char('Ethiopic Name', size=256, select=True),
        'et_code': fields.char('Ethiopic Code', size=16, select=True),
    }
