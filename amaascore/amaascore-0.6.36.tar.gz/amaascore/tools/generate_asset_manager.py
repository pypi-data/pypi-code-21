from __future__ import absolute_import, division, print_function, unicode_literals

from amaasutils.random_utils import random_string
import random

from amaascore.asset_managers.asset_manager import AssetManager
from amaascore.asset_managers.domain import Domain
from amaascore.asset_managers.enums import ASSET_MANAGER_TYPES, RELATIONSHIP_TYPES
from amaascore.asset_managers.relationship import Relationship


def generate_asset_manager(asset_manager_id=None, asset_manager_type=None, client_id=None,
                           asset_manager_status='Active'):
    asset_manager = AssetManager(asset_manager_id=asset_manager_id,
                                 asset_manager_type=asset_manager_type or random.choice(list(ASSET_MANAGER_TYPES)),
                                 client_id=client_id or random.randint(1, 2**31-1),
                                 asset_manager_status=asset_manager_status)
    return asset_manager


def generate_relationship(asset_manager_id=None, client_id=None, related_id=None, relationship_type=None):
    relationship = Relationship(asset_manager_id=asset_manager_id,
                                relationship_id=str(random.randint(1, 2**31-1)),
                                client_id=client_id or random.randint(1, 2**31-1),
                                relationship_type=relationship_type or random.choice(list(RELATIONSHIP_TYPES)),
                                related_id=related_id or random.randint(1, 2**31-1))
    return relationship

def generate_domain(asset_manager_id=None, domain=None, is_primary=True):
    domain = Domain(asset_manager_id=asset_manager_id or random.randint(1, 2**31-1),
                    domain=random_string(8) + '.com',
                    is_primary=is_primary)
    return domain
