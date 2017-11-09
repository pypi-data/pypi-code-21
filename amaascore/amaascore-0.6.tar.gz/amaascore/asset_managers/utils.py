from __future__ import absolute_import, division, print_function, unicode_literals

from amaascore.asset_managers.asset_manager import AssetManager
from amaascore.asset_managers.domain import Domain
from amaascore.asset_managers.relationship import Relationship

def json_to_asset_manager(json_asset_manager):
    asset_manager = AssetManager(**json_asset_manager)
    return asset_manager


def json_to_relationship(json_relationship):
    relationship = Relationship(**json_relationship)
    return relationship

def json_to_domain(json_domain):
    domain = Domain(**json_domain)
    return domain
