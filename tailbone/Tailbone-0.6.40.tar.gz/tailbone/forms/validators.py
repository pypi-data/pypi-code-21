# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Custom Form Validators
"""

from __future__ import unicode_literals, absolute_import

import re

from rattail.db import model
from rattail.db.util import validate_email_address, validate_phone_number
from rattail.gpc import GPC

import formencode as fe
import formalchemy as fa

from tailbone.db import Session


class ValidGPC(fe.validators.FancyValidator):
    """
    Validator for fields which should contain GPC value.
    """

    def _to_python(self, value, state):
        if value is not None:
            digits = re.sub(r'\D', '', value)
            if digits:
                try:
                    return GPC(digits)
                except ValueError as error:
                    raise fe.Invalid("Invalid UPC: {}".format(error), value, state)

    def _from_python(self, upc, state):
        if upc is None:
            return ''
        return upc.pretty()


class ModelValidator(fe.validators.FancyValidator):
    """
    Generic validator for data model reference fields.
    """
    model_class = None

    @property
    def model_name(self):
        self.model_class.__name__

    def _to_python(self, value, state):
        if value:
            obj = Session.query(self.model_class).get(value)
            if obj:
                return obj
            raise fe.Invalid("{} not found".format(self.model_name), value, state)

    def _from_python(self, value, state):
        obj = value
        if not obj:
            return ''
        return obj.uuid

    def validate_python(self, value, state):
        obj = value
        if obj is not None and not isinstance(obj, self.model_class):
            raise fe.Invalid("Value must be a valid {} object".format(self.model_name), value, state)


class ValidStore(ModelValidator):
    """
    Validator for store field.
    """
    model_class = model.Store


class ValidCustomer(ModelValidator):
    """
    Validator for customer field.
    """
    model_class = model.Customer


class ValidDepartment(ModelValidator):
    """
    Validator for department field.
    """
    model_class = model.Department


class ValidEmployee(ModelValidator):
    """
    Validator for employee field.
    """
    model_class = model.Employee


class ValidProduct(ModelValidator):
    """
    Validator for product field.
    """
    model_class = model.Product


class ValidUser(ModelValidator):
    """
    Validator for user field.
    """
    model_class = model.User


def valid_email_address(value, field=None):
    """
    FormAlchemy-compatible validation function, which leverages FormEncode
    under the hood.
    """
    if value:
        try:
            return validate_email_address(value, error=True)
        except Exception as error:
            raise fa.ValidationError(unicode(error))


def valid_phone_number(value, field=None):
    """
    FormAlchemy-compatible validation function, which leverages FormEncode
    under the hood.
    """
    if value:
        try:
            return validate_phone_number(value, error=True)
        except Exception as error:
            raise fa.ValidationError(unicode(error))
