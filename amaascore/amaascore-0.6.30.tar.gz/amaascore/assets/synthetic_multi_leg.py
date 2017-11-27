from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import date

from amaascore.assets.synthetic import Synthetic


class SyntheticMultiLeg(Synthetic):
    """
    A synthetic asset which takes multiple assets as 'legs'.  The value of the entire structure is equal to the sum of
    the legs.
    """
    def __init__(self, asset_id, asset_manager_id, legs=None, asset_issuer_id=None, asset_status='Active',
                 country_id=None, currency=None, display_name='', description='', fungible=True, issue_date=date.min,
                 maturity_date=date.max, comments=None, links=None, references=None, *args, **kwargs):
        self.legs = legs
        super(SyntheticMultiLeg, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id,
                                                fungible=fungible, asset_issuer_id=asset_issuer_id,
                                                asset_status=asset_status, currency=currency,
                                                issue_date=issue_date, maturity_date=maturity_date,
                                                country_id=country_id, roll_price=False,
                                                display_name=display_name, description=description,
                                                comments=comments, links=links, references=references,
                                                *args, **kwargs)

    @property
    def legs(self):
        if hasattr(self, '_legs'):
            return self._legs

    @legs.setter
    def legs(self, legs):
        """
        A list of dictionaries of the legs that make up the multi-legged asset.
        Format is {'asset_id': XYZ, 'quantity': ABC_Decimal}
        :param legs:
        :return:
        """
        if legs is not None:
            if not isinstance(legs, list):
                raise ValueError("Invalid type for asset legs: %s" % type(legs).__name__)
            if not all([isinstance(leg, dict) for leg in legs]):
                raise ValueError("All asset legs must be dictionaries")
            self._legs = legs
