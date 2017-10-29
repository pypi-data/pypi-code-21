# -*- coding:utf-8 -*-
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

from openerp import fields, models


class ResPartner(models.Model):

    _inherit = 'res.partner'

    # fields
    #
    ethiopic_name = fields.Char(size=1024, index=True)
    subcity = fields.Char(string='Subcity (Woreda)', size=256, index=True)
    kebele = fields.Char(size=8, index=True)
    houseno = fields.Char(string='House No', size=16, index=True)
    et_subcity = fields.Char(
        string='Amharic Subcity (Woreda)', size=256, index=True)
    et_city = fields.Char(string='Amharic City', size=256, index=True)
    pobox = fields.Char(string='P.O. Box', size=16)
