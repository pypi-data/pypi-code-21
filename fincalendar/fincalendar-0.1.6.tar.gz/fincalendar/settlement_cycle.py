from __future__ import absolute_import, division, print_function, unicode_literals

from fincalendar.equity_config import EQUITY_SETTLEMENT_CYCLE, EXCHANGE_SETTLEMENT_CYCLE_OVERRIDES
from fincalendar.foreign_exchange_config import FX_SPOT_SETTLEMENT_CYCLE, FX_SPOT_CROSS_SETTLEMENT_CYCLE
from fincalendar.currency_countrycode_mapping import countrycode_to_currency


def get_settlement_cycles(asset_class):
    """ Returns settlement cycle configuration for an asset_class """
    if asset_class.upper() == 'EQUITY':
        return {'settlement_cycle': EQUITY_SETTLEMENT_CYCLE,
                'exchange_settlement_cycle_overrides': EXCHANGE_SETTLEMENT_CYCLE_OVERRIDES}

    if asset_class.upper == 'FX_SPOT':
        return {'settlement_cycle': FX_SPOT_SETTLEMENT_CYCLE,
                'cross_settlement_exception_case': FX_SPOT_CROSS_SETTLEMENT_CYCLE}
    # Add additional asset classes here
    raise NotImplementedError("This asset class is not yet configured")


def get_country_settlement_cycle(asset_class, country_code):
    if asset_class.upper() == 'EQUITY':
        settlement_cycle = EQUITY_SETTLEMENT_CYCLE.get(country_code)
        if not settlement_cycle:
            raise NotImplementedError("This country/asset class combination is not yet configured")        
        return settlement_cycle



    if asset_class.upper() == 'FX_SPOT':
        settlement_cycle = FX_SPOT_SETTLEMENT_CYCLE.get(countrycode_to_currency(country_code))
        if not settlement_cycle:
            raise NotImplementedError("This country/asset class combination is not yet configured")
        return settlement_cycle


    # Add additional asset classes here
    raise NotImplementedError("This asset class is not yet configured")






# TODO - Add an exchange-level settlement cycle
