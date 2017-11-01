# -*- coding: utf-8 -*-

import re

from cerberus import Validator as BaseValidator


class Validator(BaseValidator):

    def _validate_type_objectid(self, value):
        if self.SCHEMA.get('nullable') and value is None:
            return True

        if re.match('[a-f0-9]{24}', str(value)):
            return True
