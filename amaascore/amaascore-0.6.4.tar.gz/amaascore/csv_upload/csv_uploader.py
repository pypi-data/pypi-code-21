import logging.config
import csv
import json

from amaascore.tools.csv_tools import csv_stream_to_objects
from amaasutils.logging_utils import DEFAULT_LOGGING
from amaascore.csv_upload.utils import process_normal, interface_direct_class, interface_direct_csvpath

from amaascore.assets.asset import Asset
from amaascore.assets.automobile import Automobile
from amaascore.assets.bond import BondCorporate, BondGovernment, BondMortgage
from amaascore.assets.bond_future import BondFuture
from amaascore.assets.bond_future_option import BondFutureOption
from amaascore.assets.bond_option import BondOption
from amaascore.assets.commodity_future import CommodityFuture
from amaascore.assets.cfd import ContractForDifference
from amaascore.assets.currency import Currency
from amaascore.assets.custom_asset import CustomAsset
from amaascore.assets.derivative import Derivative
from amaascore.assets.energy_future import EnergyFuture
from amaascore.assets.equity import Equity
from amaascore.assets.equity_future import EquityFuture
from amaascore.assets.etf import ExchangeTradedFund
from amaascore.assets.foreign_exchange import ForeignExchange, NonDeliverableForward
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
from amaascore.assets.option_mixin import OptionMixin
from amaascore.assets.real_asset import RealAsset
from amaascore.assets.real_estate import RealEstate
from amaascore.assets.sukuk import Sukuk
from amaascore.assets.synthetic import Synthetic
from amaascore.assets.synthetic_from_book import SyntheticFromBook
from amaascore.assets.synthetic_multi_leg import SyntheticMultiLeg
from amaascore.assets.wine import Wine
from amaascore.assets.warrants import Warrant

from amaascore.parties.broker import Broker
from amaascore.parties.company import Company
from amaascore.parties.exchange import Exchange
from amaascore.parties.fund import Fund
from amaascore.parties.government_agency import GovernmentAgency
from amaascore.parties.individual import Individual
from amaascore.parties.organisation import Organisation
from amaascore.parties.party import Party
from amaascore.parties.sub_fund import SubFund

from amaascore.books.book import Book

from amaascore.corporate_actions.corporate_action import CorporateAction
from amaascore.corporate_actions.dividend import Dividend
from amaascore.corporate_actions.notification import Notification
from amaascore.corporate_actions.split import Split

from amaascore.market_data.eod_price import EODPrice
from amaascore.market_data.fx_rate import FXRate
from amaascore.market_data.quote import Quote

from amaascore.transactions.position import Position
from amaascore.transactions.transaction import Transaction

from amaascore.asset_managers.asset_manager import AssetManager
from amaascore.asset_managers.relationship import Relationship

class Uploader(object):

    def __init__(self):
        pass

    @staticmethod
    def json_handler(orderedDict, params):
        Dict = dict(orderedDict)
        for key, var in params.items():
            Dict[key]=var
        data_class = Dict.get('amaasclass', None)
        Dict = process_normal(Dict)
        obj = globals()[data_class](**dict(Dict))
        return obj

    @staticmethod
    def upload(csvpath, asset_manager_id=None, client_id=None):
        """convert csv file rows to objects and insert;
           asset_manager_id and possibly client_id from the UI (login)"""
        interface = interface_direct_csvpath(csvpath)
        logging.config.dictConfig(DEFAULT_LOGGING)
        logger = logging.getLogger(__name__)
        if asset_manager_id is None:
            params = dict()
        elif client_id is None:
            params = {'asset_manager_id': asset_manager_id}
        else:
            params = {'asset_manager_id': asset_manager_id, 'client_id': client_id}
        with open(csvpath) as csvfile:
            objs = csv_stream_to_objects(stream=csvfile, json_handler=Uploader.json_handler, params=params)
        for obj in objs:
            interface.new(obj)
            logger.info('Creating this object and upload to database successfully')

    @staticmethod
    def download(csvpath, asset_manager_id, data_id_type, data_id_list):
        """retrieve the objs mainly for test purposes"""
        interface = interface_direct_csvpath(csvpath)
        logging.config.dictConfig(DEFAULT_LOGGING)
        logger = logging.getLogger(__name__)
        objs = []
        for data_id in data_id_list:
            Dict = dict()
            Dict[data_id_type] = data_id
            objs.append(interface.retrieve(asset_manager_id=asset_manager_id, **Dict))
        return objs