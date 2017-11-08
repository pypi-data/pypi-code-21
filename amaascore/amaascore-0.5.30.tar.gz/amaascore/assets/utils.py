from __future__ import absolute_import, division, print_function, unicode_literals

import inspect

#  All possible class names must be inserted into the globals collection.
#  If there is a better way of doing this, please suggest!
from amaascore.assets.asset import Asset
from amaascore.assets.bond import BondCorporate, BondGovernment, BondMortgage
from amaascore.assets.bond_future import BondFuture
from amaascore.assets.bond_future_option import BondFutureOption
from amaascore.assets.bond_option import BondOption
from amaascore.assets.commodity_future import CommodityFuture
from amaascore.assets.cfd import ContractForDifference
from amaascore.assets.cryptocurrency import Cryptocurrency
from amaascore.assets.currency import Currency
from amaascore.assets.custom_asset import CustomAsset
from amaascore.assets.derivative import Derivative
from amaascore.assets.energy_future import EnergyFuture
from amaascore.assets.equity import Equity
from amaascore.assets.equity_future import EquityFuture
from amaascore.assets.etf import ExchangeTradedFund
from amaascore.assets.foreign_exchange import ForeignExchange, ForeignExchangeForward, ForeignExchangeSpot
from amaascore.assets.fund import Fund
from amaascore.assets.future import Future
from amaascore.assets.future_option import FutureOption
from amaascore.assets.fx_future import ForeignExchangeFuture
from amaascore.assets.fx_option import ForeignExchangeOption
from amaascore.assets.index import Index
from amaascore.assets.index_future import IndexFuture
from amaascore.assets.interest_rate_future import InterestRateFuture
from amaascore.assets.listed_cfd import ListedContractForDifference
from amaascore.assets.listed_derivative import ListedDerivative
from amaascore.assets.real_asset import RealAsset
from amaascore.assets.real_estate import RealEstate
from amaascore.assets.sukuk import Sukuk
from amaascore.assets.synthetic import Synthetic
from amaascore.assets.synthetic_from_book import SyntheticFromBook
from amaascore.assets.synthetic_multi_leg import SyntheticMultiLeg
from amaascore.assets.wine import Wine
from amaascore.assets.automobile import Automobile
from amaascore.assets.warrants import Warrant
from amaascore.assets.private_investment import PrivateInvestment

def json_to_asset(json_asset):
    # Iterate through the asset children, converting the various JSON attributes into the relevant class type
    for (collection_name, clazz) in Asset.children().items():
        children = json_asset.pop(collection_name, {})
        collection = {}
        for (child_type, child_json) in children.items():
            # Handle the case where there are multiple children for a given type - e.g. links
            if isinstance(child_json, list):
                child = set()
                for child_json_in_list in child_json:
                    child.add(clazz(**child_json_in_list))
            else:
                child = clazz(**child_json)
            collection[child_type] = child
        json_asset[collection_name] = collection
    clazz = globals().get(json_asset.get('asset_type'))
    if not clazz:
        raise ValueError('Missing Asset Type: %s' % json_asset.get('asset_type'))
    args = inspect.getargspec(clazz.__init__)
    # Some fields are always added in, even though they're not explicitly part of the constructor
    clazz_args = args.args + clazz.amaas_model_attributes()
    # is not None is important so it includes zeros and False
    constructor_dict = {arg: json_asset.get(arg) for arg in clazz_args
                        if json_asset.get(arg) is not None and arg != 'self'}
    asset = clazz(**constructor_dict)
    return asset
