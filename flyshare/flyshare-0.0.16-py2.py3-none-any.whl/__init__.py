__version__ = '0.0.16'
__author__ = 'Rubing Duan'

"""
for trading data
"""
from flyshare.stock.trading import (get_hist_data, get_tick_data, get_today_all, get_large_order, get_index, get_h_data,
                                    get_realtime_quotes)

"""
for fundamental data
"""
from flyshare.stock.fundamental import (get_stock_basics, get_report_data,get_balance_sheet,get_cash_flow,
                                        get_debtpaying_data, get_cashflow_data,get_growth_data,get_operation_data,
                                         get_profit_data,get_profit_statement)

"""
for data source
"""
from flyshare.util.conn import (get_apis, close_apis)

from flyshare.stock.menu_datasource import (set_datasource)