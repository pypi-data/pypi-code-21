from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
from dateutil.parser import parse
import sys
import uuid

from amaascore.core.amaas_model import AMaaSModel
from amaascore.core.reference import Reference

# This extremely ugly hack is due to the whole Python 2 vs 3 debacle.
type_check = str if sys.version_info >= (3, 0, 0) else (str, unicode)


class CorporateAction(AMaaSModel):

    @staticmethod
    def children():
        return {'references': Reference}

    def __init__(self, asset_manager_id, corporate_action_id, record_date, corporate_action_status='Open',
                 asset_id=None, party_id=None, declared_date=None, settlement_date=None, elective=False, message=None,
                 description='', references=None, *args, **kwargs):
        self.asset_manager_id = asset_manager_id
        self.corporate_action_id = corporate_action_id or uuid.uuid4().hex
        self.corporate_action_type = self.__class__.__name__
        self.corporate_action_status = corporate_action_status
        self.record_date = record_date
        self.declared_date = declared_date or datetime.date.today()
        self.settlement_date = settlement_date or self.record_date
        self.asset_id = asset_id
        self.party_id = party_id
        self.elective = elective
        self.message = message
        self.description = description
        # Defaults are here not in constructor for mutability reasons.
        self.references = references.copy() if references else {}
        self.references['Argomi'] = Reference(reference_value=self.corporate_action_id)  # Upserts the Argomi Reference

        super(CorporateAction, self).__init__(*args, **kwargs)

    @property
    def record_date(self):
        if hasattr(self, '_record_date'):
            return self._record_date

    @record_date.setter
    def record_date(self, value):
        """
        The date on which the corporate action takes effect
        :param value:
        :return:
        """
        if value:
            self._record_date = parse(value).date() if isinstance(value, type_check) else value

    @property
    def declared_date(self):
        if hasattr(self, '_record_date'):
            return self._record_date

    @declared_date.setter
    def declared_date(self, value):
        """
        The date on which the corporate action was declared
        :param value:
        :return:
        """
        if value:
            self._declared_date = parse(value).date() if isinstance(value, type_check) else value

    @property
    def settlement_date(self):
        if hasattr(self, '_settlement_date'):
            return self._settlement_date

    @settlement_date.setter
    def settlement_date(self, value):
        """
        The date on which the corporate action is settled
        :param value:
        :return:
        """
        if value:
            self._settlement_date = parse(value).date() if isinstance(value, type_check) else value
