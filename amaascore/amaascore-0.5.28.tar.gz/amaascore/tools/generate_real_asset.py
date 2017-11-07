from __future__ import absolute_import, division, print_function, unicode_literals

from amaasutils.random_utils import random_string, random_date
import random

from amaascore.assets.enums import WINE_CLASSIFICATIONS, WINE_PACKING_TYPE
from amaascore.assets.wine import Wine
from amaascore.core.comment import Comment
from amaascore.tools.generate_asset import generate_common


def generate_wine(asset_manager_id=None, asset_id=None):
    props = generate_common(asset_manager_id=asset_manager_id, asset_id=asset_id)
    wine = Wine(year=random_date(start_year=1950, end_year=2016),
                producer=random_string(5),
                region=random.choice(['Bordeaux', 'Burgundy', 'Tuscany', 'Napa Valley']),
                appellation=random.choice([None]*3 + ['Côtes du Rhône', 'Graves', 'Saint-Émilion']),
                classification=random.choice(list(WINE_CLASSIFICATIONS)),
                color=random.choice(['Red', 'White']),
                bottle_size=random.choice(['0.75L']*3 + ['1.5L']),
                bottle_in_cellar=random.choice([True]*3 + [False]),
                bottle_location=random_string(20),
                storage_cost=None,
                rating_type='Parker',
                rating_value=random.randint(93, 100),
                packing_type=random.choice(list(WINE_PACKING_TYPE)),
                to_drink_start=random_date(start_year=2000),
                to_drink_end=random_date(end_year=2050),
                comments = {'DrinkingNotes': Comment(comment_value=random_string(100))},
                **props)
    return wine
