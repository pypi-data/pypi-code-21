from __future__ import absolute_import, division, print_function, unicode_literals

from amaascore.corporate_actions.corporate_action import CorporateAction


class Notification(CorporateAction):

    def __init__(self, asset_manager_id, corporate_action_id, record_date, corporate_action_status='Open',
                 asset_id=None, party_id=None, declared_date=None, settlement_date=None, elective=False, message=None,
                 description='', references=None, *args, **kwargs):
        super(Notification, self).__init__(asset_manager_id=asset_manager_id, corporate_action_id=corporate_action_id,
                                           record_date=record_date, corporate_action_status=corporate_action_status,
                                           asset_id=asset_id, party_id=party_id, declared_date=declared_date,
                                           settlement_date=settlement_date, elective=elective, message=message,
                                           description=description, references=references, *args, **kwargs)
