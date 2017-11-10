from __future__ import absolute_import, division, print_function, unicode_literals

from amaascore.assets.currency import CurrencyBase
from amaascore.assets.enums import CRYPTOCURRENCY_PROOF_TYPES


class Cryptocurrency(CurrencyBase):

    def __init__(self, asset_id, asset_manager_id=0, asset_status='Active', proof_type='Proof of Work',
                 max_supply=None, display_name='', minor_unit_places=8, description='', country_id=None,
                 *args, **kwargs):
        self.proof_type = proof_type
        self.max_supply = max_supply
        super(Cryptocurrency, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id,
                                             display_name=display_name,
                                             minor_unit_places=minor_unit_places,
                                             asset_status=asset_status, description=description,
                                             country_id=country_id, *args, **kwargs)

    @property
    def max_supply(self):
        if hasattr(self, '_max_supply'):
            return self._max_supply

    @max_supply.setter
    def max_supply(self, max_supply):
        """
        :param max_supply:
        :return:
        """
        self._max_supply = max_supply

    @property
    def proof_type(self):
        return self._proof_type

    @proof_type.setter
    def proof_type(self, proof_type):
        """
        :param proof_type:
        :return:
        """
        if proof_type in CRYPTOCURRENCY_PROOF_TYPES:
            self._proof_type = proof_type
        else:
            raise ValueError("Invalid input for proof type: %s" % proof_type)
