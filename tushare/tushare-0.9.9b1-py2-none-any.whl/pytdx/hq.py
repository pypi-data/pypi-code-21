# coding=utf-8

#
# Just for practising
#


import os
import socket
import sys
import pandas as pd

if __name__ == '__main__':
    sys.path.append(os.path.dirname(
        os.path.dirname(os.path.realpath(__file__))))

from pytdx.log import DEBUG, log
from pytdx.parser.get_security_bars import GetSecurityBarsCmd
from pytdx.parser.get_security_quotes import GetSecurityQuotesCmd
from pytdx.parser.get_security_count import GetSecurityCountCmd
from pytdx.parser.get_security_list import GetSecurityList
from pytdx.parser.get_index_bars import GetIndexBarsCmd
from pytdx.parser.get_minute_time_data import GetMinuteTimeData
from pytdx.parser.get_history_minute_time_data import GetHistoryMinuteTimeData
from pytdx.parser.get_transaction_data import GetTransactionData
from pytdx.parser.get_history_transaction_data import GetHistoryTransactionData
from pytdx.parser.get_company_info_category import GetCompanyInfoCategory
from pytdx.parser.get_company_info_content import GetCompanyInfoContent
from pytdx.parser.get_xdxr_info import GetXdXrInfo
from pytdx.parser.get_finance_info import GetFinanceInfo
from pytdx.parser.get_block_info import GetBlockInfo, GetBlockInfoMeta, get_and_parse_block_info
from pytdx.util import get_real_trade_date, trade_date_sse
from pytdx.params import TDXParams
from pytdx.heartbeat import HqHeartBeatThread

from pytdx.parser.setup_commands import SetupCmd1, SetupCmd2, SetupCmd3
import threading
import datetime
import random

from pytdx.base_socket_client import BaseSocketClient, update_last_ack_time


class TdxHq_API(BaseSocketClient):

    def setup(self):
        SetupCmd1(self.client).call_api()
        SetupCmd2(self.client).call_api()
        SetupCmd3(self.client).call_api()

    # API List

    # Notice：，如果一个股票当天停牌，那天的K线还是能取到，成交量为0
    @update_last_ack_time
    def get_security_bars(self, category, market, code, start, count):
        cmd = GetSecurityBarsCmd(self.client, lock=self.lock)
        cmd.setParams(category, market, code, start, count)
        return cmd.call_api()

    @update_last_ack_time
    def get_index_bars(self, category, market, code, start, count):
        cmd = GetIndexBarsCmd(self.client, lock=self.lock)
        cmd.setParams(category, market, code, start, count)
        return cmd.call_api()

    @update_last_ack_time
    def get_security_quotes(self, all_stock):
        cmd = GetSecurityQuotesCmd(self.client, lock=self.lock)
        cmd.setParams(all_stock)
        return cmd.call_api()

    @update_last_ack_time
    def get_security_count(self, market):
        cmd = GetSecurityCountCmd(self.client, lock=self.lock)
        cmd.setParams(market)
        return cmd.call_api()

    @update_last_ack_time
    def get_security_list(self, market, start):
        cmd = GetSecurityList(self.client, lock=self.lock)
        cmd.setParams(market, start)
        return cmd.call_api()

    @update_last_ack_time
    def get_minute_time_data(self, market, code):
        cmd = GetMinuteTimeData(self.client, lock=self.lock)
        cmd.setParams(market, code)
        return cmd.call_api()

    @update_last_ack_time
    def get_history_minute_time_data(self, market, code, date):
        cmd = GetHistoryMinuteTimeData(self.client, lock=self.lock)
        cmd.setParams(market, code, date)
        return cmd.call_api()

    @update_last_ack_time
    def get_transaction_data(self, market, code, start, count):
        cmd = GetTransactionData(self.client, lock=self.lock)
        cmd.setParams(market, code, start, count)
        return cmd.call_api()

    @update_last_ack_time
    def get_history_transaction_data(self, market, code, start, count, date):
        cmd = GetHistoryTransactionData(self.client, lock=self.lock)
        cmd.setParams(market, code, start, count, date)
        return cmd.call_api()

    @update_last_ack_time
    def get_company_info_category(self, market, code):
        cmd = GetCompanyInfoCategory(self.client, lock=self.lock)
        cmd.setParams(market, code)
        return cmd.call_api()

    @update_last_ack_time
    def get_company_info_content(self, market, code, filename, start, length):
        cmd = GetCompanyInfoContent(self.client, lock=self.lock)
        cmd.setParams(market, code, filename, start, length)
        return cmd.call_api()

    @update_last_ack_time
    def get_xdxr_info(self, market, code):
        cmd = GetXdXrInfo(self.client, lock=self.lock)
        cmd.setParams(market, code)
        return cmd.call_api()

    @update_last_ack_time
    def get_finance_info(self, market, code):
        cmd = GetFinanceInfo(self.client, lock=self.lock)
        cmd.setParams(market, code)
        return cmd.call_api()


    @update_last_ack_time
    def get_block_info_meta(self, blockfile):
        cmd = GetBlockInfoMeta(self.client, lock=self.lock)
        cmd.setParams(blockfile)
        return cmd.call_api()

    @update_last_ack_time
    def get_block_info(self, blockfile, start, size):
        cmd = GetBlockInfo(self.client, lock=self.lock)
        cmd.setParams(blockfile, start, size)
        return cmd.call_api()

    def get_and_parse_block_info(self, blockfile):
        return get_and_parse_block_info(self, blockfile)


    def do_heartbeat(self):
        self.get_security_count(random.randint(0, 1))


    

if __name__ == '__main__':
    import pprint

    api = TdxHq_API()
    if api.connect('222.161.249.156', 7709):
#         data = api.get_index_bars(9, 1, '000001', 1, 2)
        data = api.get_history_transaction_data(TDXParams.MARKET_SZ, '000001', 0, 10, 20170209)
        
        pprint.pprint(data)
        
        api.disconnect()
