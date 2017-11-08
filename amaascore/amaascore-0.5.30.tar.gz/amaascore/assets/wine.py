from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import date
from dateutil.parser import parse
import sys

from amaascore.assets.real_asset import RealAsset

# This extremely ugly hack is due to the whole Python 2 vs 3 debacle.
type_check = str if sys.version_info >= (3, 0, 0) else (str, unicode)


class Wine(RealAsset):

    def __init__(self, asset_manager_id, asset_id, year=None, producer=None,
                 region=None, appellation=None, classification=None, color=None, bottle_size=None,
                 bottle_in_cellar=None, bottle_location=None, storage_cost=None, rating_type=None,
                 rating_value=None, packing_type=None, to_drink_start=None, to_drink_end=None,
                 asset_issuer_id=None, asset_status='Active', display_name='', description='',
                 country_id=None, venue_id=None, currency=None, issue_date=date.min, ownership=None,
                 comments=None, links=None, references=None, *args, **kwargs):
        self.year = year
        self.producer = producer
        self.region = region
        self.appellation = appellation
        self.classification = classification
        self.color = color
        self.bottle_size = bottle_size
        self.bottle_in_cellar = bottle_in_cellar
        self.bottle_location = bottle_location
        self.storage_cost = storage_cost
        self.rating_type = rating_type
        self.rating_value = rating_value
        self.packing_type = packing_type
        self.to_drink_start = to_drink_start
        self.to_drink_end = to_drink_end
        super(Wine, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id,
                                   asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                   display_name=display_name, description=description,
                                   country_id=country_id, venue_id=venue_id, issue_date=issue_date,
                                   currency=currency, ownership=ownership,
                                   comments=comments, links=links, references=references,
                                   *args, **kwargs)

    @property
    def year(self):
        if hasattr(self, '_year'):
            return self._year

    @year.setter
    def year(self, year):
        if isinstance(year, type_check):
            year = int(year)
        self._year = year

    @property
    def to_drink_start(self):
        if hasattr(self, '_to_drink_start'):
            return self._to_drink_start

    @to_drink_start.setter
    def to_drink_start(self, to_drink_start):
        if isinstance(to_drink_start, (type_check)):
            to_drink_start = parse(to_drink_start).date()
        self._to_drink_start = to_drink_start

    @property
    def to_drink_end(self):
        if hasattr(self, '_to_drink_end'):
            return self._to_drink_end

    @to_drink_end.setter
    def to_drink_end(self, to_drink_end):
        if isinstance(to_drink_end, (type_check)):
            to_drink_end = parse(to_drink_end).date()
        self._to_drink_end = to_drink_end

