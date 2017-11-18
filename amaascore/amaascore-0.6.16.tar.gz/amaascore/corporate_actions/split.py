from __future__ import absolute_import, division, print_function, unicode_literals

from amaascore.corporate_actions.corporate_action import CorporateAction


class Split(CorporateAction):

    def __init__(self, asset_manager_id, corporate_action_id, record_date, ratio, corporate_action_status='Open',
                 asset_id=None, party_id=None, declared_date=None, settlement_date=None, elective=False, message=None,
                 description='', references=None, *args, **kwargs):
        self.ratio = ratio
        super(Split, self).__init__(asset_manager_id=asset_manager_id, corporate_action_id=corporate_action_id,
                                    record_date=record_date, corporate_action_status=corporate_action_status,
                                    asset_id=asset_id, party_id=party_id, declared_date=declared_date,
                                    settlement_date=settlement_date, elective=elective, message=message,
                                    description=description, references=references, *args, **kwargs)

    @property
    def ratio(self):
        if hasattr(self, '_ratio'):
            return self._ratio

    @ratio.setter
    def ratio(self, ratio):
        """
        The split ratio of the corporate action - i.e. the ratio of new shares to old shares
        :param ratio: A tuple representing (original_count, new_count).  For example (1, 2) is a doubling stock split.
        (3, 1) is a 3:1 reverse stock split.
        :return:
        """
        if isinstance(ratio, tuple):
            self._ratio = ratio
        else:
            raise TypeError('Invalid ratio type: %s' % type(ratio))
