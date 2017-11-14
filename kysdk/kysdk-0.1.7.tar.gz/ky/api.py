import json
import time
import base64
import urllib.request


class Api:

    def __init__(self, url, username='', password=''):
        basic = username + ':' + password
        auth = base64.b64encode(basic.encode(encoding='utf-8')).decode('utf-8')
        self.url = url
        self.headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': 'Basic ' + auth
        }
        self.id = 0

    def call(self, func, params):
        self.id = self.id + 1
        req_id = self.id
        payload = {
            "method": func,
            "params": params,
            "jsonrpc": "2.0",
            "id": req_id,
        }
        req = urllib.request.Request(self.url, method='POST', data=json.dumps(payload).encode('utf-8'), headers=self.headers)
        res = urllib.request.urlopen(req)
        if res.status != 200:
            raise Exception(res.resean)
        response = json.loads(res.read().decode('utf-8'))
        if 'error' in response:
            raise Exception(response['error'])
        return response['result']

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]

        def func(*args):
            return self.call(name, args)
        return func

    def get_all_info(self, fields='*'):
        """请求全部股票信息

        [可以根据fields指定获取的字段]

        Keyword Arguments:
            fields {str} -- [description] (default: {'*'})

        Returns:
            [type] -- list of dict
        """
        return self.call('get_all_info', [fields])

    def get_stockinfo(self, symbols=None, field=None):
        """请求股票信息
        [可以根据symbols指定股票代码列表, 根据field指定获取的字段]

        Keyword Arguments:
            symbols {list} -- [description] (default: {None})
            field {list} -- [description] (default: {None})

        Returns:
            [type] -- list of dict
        """
        return self.call('get_stockinfo', [symbols, field])

    def get_share_float(self, start, end, num_days, symbols=None, field=None):
        """根据起始截止日期和股票代码列表以及指定获取的字段请求股票信息

        Arguments:

        """
        return self.call('get_share_float', [start, end, num_days, symbols, field])

    def get_trading_dates_by_date_range(self, end, start, exchange='sh'):
        """获取指定日期内的交易日

        [description]

        Arguments:
            start {[type]} -- [description]
            end {[type]} -- [description]

        Keyword Arguments:
            exchange {str} -- [description] (default: {'sh'})

        Returns:
            [type] -- [type] -- list of str like ['2016-01-01']
        """
        return self.call('get_trading_dates_by_date_range', [end, start, exchange])

    def get_symbols_by_industry(self, industry):
        """根据行业获取股票代码

        [description]

        Arguments:
            industry {[type]} -- [行业名称]

        Returns:
            [type] -- list of str(symbols)
        """
        return self.call('get_symbols_by_industry', [industry])

    def get_industries(self):
        """获取所有行业的名称列表

        [description]

        Arguments:

        Returns:
            [type] -- list of str
        """
        return self.call('get_industries', [])

    def get_symbols_by_concept(self, concept):
        """根据概念获取股票代码

        [description]

        Arguments:
            industry {[type]} -- [行业名称]

        Returns:
            [type] -- list of str(symbols)
        """
        return self.call('get_symbols_by_concept', [concept])

    def get_concepts(self):
        """获取所有概念的名称列表

        [description]

        Arguments:

        Returns:
            [type] -- list of str(concepts)

        """
        return self.call('get_concepts', [])

    def get_symbols_by_index(self, index):
        """根据股票标签获取股票代码
        ！！待完善
        支持
            hs300s : 沪深300
            sz50s  : 上证50成份股
            zz500s : 中证500成份股
        Arguments:
            index {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        return self.call('get_symbols_by_index', [index])

    def get_indices(self):
        """获得所有指数的信息列表

        [description]

        Arguments:

        Returns:
            [type] -- list of dict
        """
        return self.call('get_indices', [])


    def get_all_symbols_by_date(self, date):
        """获取指定交易日上市的股票代码列表
        Arguments:
            date {[type]} -- [description]
        Returns:
            [type] -- list of str (symbol)
        """
        return self.call('get_all_symbols_by_date', [date])

    def get_trading_days(self, start, end, num_days, exchange='sh'):
        """获取指定日期内的交易日

        [description]

        Arguments:
            start {str} -- 开始日期
            end {str} -- 截止日期
            num_days {str} -- 倒数天数

        Keyword Arguments:
            exchange {str} -- [description] (default: {'sh'})

        Returns:
            [type] -- [type] -- list of str like ['2016-01-01']
                """
        return self.call('get_trading_days', [start, end, num_days, exchange])

    def get_last_dailybars_by_date(self, symbol, num, endDate=None, adjType='qfq'):
        """获取最近几天的日线，16:00后包含当天
        Arguments:
            symbol {str} -- 股票代码
            num {int} -- 天数

        Keyword Arguments:
            endDate {[type]} -- [description] (default: {None})
            adjType {str} -- [description] (default: {'none'})

        Returns:
            [type] -- list of dict
        """
        return self.call('get_last_dailybars_by_date', [symbol, num, endDate, adjType])

    def get_dailybars_by_date_range(self, start, end, symbols=None, adjType='qfq'):
        """获取指定日期的日线，不包含当天
            必须指定股票代码，否则返回空列表
            时间区间不大于1个月（31天）
        Arguments:
            start {str} -- 开始日期
            end {str} -- 结束日期
            symbols {list} -- 股票代码列表

        Keyword Arguments:
            adjType {str} -- 复权类型 (default: {'none'})

        Returns:
            [type] -- list of dict
        """
        return self.call('get_dailybars_by_date_range', [start, end, symbols, adjType])

    def get_daily_bars(self, symbol, start, end, adjType='qfq'):
        """获取单只股票交易bar
            支持超过30天
        Arguments:
            symbol {[type]} -- 股票代码
            start {str} -- 开始日期
            end {str} -- 结束日期

        Keyword Arguments:
            adjType {str} -- [description] (default: {'none'})

        Returns:
            [type] -- list of dict
        """
        return self.call('get_daily_bars', [symbol, start, end, adjType])

    def get_bars_by_date(self, symbols, date):
        """获取多只股票指定日的交易数据
        Arguments:
            symbols {list} -- 股票代码列表
            date {[type]} -- [description]
        Returns:
            [type] -- [description]
        """
        return self.call('get_bars_by_date', [symbols, date])

    def get_bars_of_date(self, date, isOpen=1):
        """获取指定交易日的全部股票行情

        Arguments:
            date {str} -- 日期

        Keyword Arguments:
            isOpen {number} -- 是否包含停牌股票（使用上一日） (default: {1})

        Returns:
            [type] -- [description]
        """
        return self.call('get_quotations_of_date', [date, isOpen])

    def get_stock_trading_statics_by_date(self, symbol, end_date=None):
        return self.call('get_stock_trading_statics_by_date', [symbol, end_date])

    def get_all_stock_trading_statics_by_date(self, end_date):
        return self.call('get_all_stock_trading_statics_by_date', [end_date])

    def get_dailybars(self, end, start=None, symbols=None, adjType='none', field=None):
        """根据日期范围和股票代码列表，请求日线
        Arguments:
            end {str} -- 结束日期

        Keyword Arguments:
            start {str} -- 开始日期
            symbols {list} -- 股票代码列表
            adjType {str} -- 复权类型
            field {list} -- 返回字段列表

        Returns:
            {list} -- 日线列表
        """
        return self.call('get_dailybars', [end, start, symbols, adjType, field])

    def get_last_n_dailybars(self, symbol, end, num_days=1, adjType='none', fields=None):
        """返回单只股票最后n个交易日日线
        Arguments:
            symbol {str} -- 股票symbol
            end {str} -- 结束日期
        
        Keyword Arguments:
            num_days {int} -- 倒数交易日
            adjType {str} -- 复权类型
            fields {list} -- 返回字段列表
        """
        return self.call('get_last_n_dailybars', [symbol, end, num_days, adjType, fields])
    
    def get_dailybars_of_stock(self, symbol, end=None, start=None, num_days=None, adjType='none'):
        """返回单只股票的所有日线
        Arguments:
            symbol {str} -- 股票symbol
        
        Keyword Arguments:
            end {str} -- 截止日期
            start {str} -- 开始日期
            num_days {int} -- 倒数交易日
            adjType {str} -- 复权类型
        """
        return self.call('get_dailybars_of_stock', [symbol, end, start, num_days, adjType])

    def get_management_trade(self, end, start, symbols=None, field=None):
        """返回高管增减持
        Arguments:
            end {str} -- 截止日期
            start {str} -- 开始日期
        
        Keyword Arguments:
            symbols {list} -- 股票symbols
            field {list} -- 返回字段列表
        """
        return self.call('get_management_trade', [end, start, symbols, field])

    def get_index_dailybars(self, end, start=None, symbols=None):
        """根据日期范围和指数代码列表，请求日线
        Arguments:
            end {str} -- 结束日期

        Keyword Arguments:
            start {str} -- 开始日期
            symbols {list} -- 股票代码列表

        Returns:
            {list} -- 日线列表
        """
        return self.call('get_index_dailybars', [end, start, symbols])

    def get_fin_bs(self, end, start, reportType, symbols=None, field=None):
        """根据开始和截止日期(含)和表类型获取股票代码列表的资产负债表
        Arguments:
            start {str} -- 开始日期
            end {str} -- 截止日期
            reportType {str} -- 报表类型(一季度,半年度,三季度,年度)

        Keyword Arguments:
            symbols {list} -- 股票代码列表
            field {list} -- 返回值字段
        """
        return self.call('get_fin_bs', [end, start, reportType, symbols, field])

    def get_fin_is(self, end, start, reportType, symbols=None, field=None):
        """根据开始和截止日期(含)和表类型获取股票代码列表的利润表
        Arguments:
            start {str} -- 开始日期
            end {str} -- 截止日期
            reportType {str} -- 报表类型(一季度,半年度,三季度,年度)

        Keyword Arguments:
            symbols {list} -- 股票代码列表
            field {list} -- 返回值字段
        """
        return self.call('get_fin_is', [end, start, reportType, symbols, field])

    def get_fin_cf(self, end, start, reportType, symbols=None, field=None):
        """根据开始和截止日期(含)和表类型获取股票代码列表的现金流量表
        Arguments:
            start {str} -- 开始日期
            end {str} -- 截止日期
            reportType {str} -- 报表类型(一季度,半年度,三季度,年度)

        Keyword Arguments:
            symbols {list} -- 股票代码列表
            field {list} -- 返回值字段
        """
        return self.call('get_fin_cf', [end, start, reportType, symbols, field])
    

    def get_majorholder_trade(self, end, start, symbols=None, field=None):
        """根据股东增减持公告的开始和截止日期和股票代码列表获得股东增减持
        Arguments:
            end {str} -- 截止日期
            start {str} -- 开始日期

        Keyword Arguments:
            symbols {list} -- 股票代码列表
            field {list} -- 返回值字段
        """
        return self.call('get_majorholder_trade', [end, start, symbols, field])

    def get_stock_analysis(self, end, start=None, symbols=None):
        """根据开始和截止日期和倒数天数和股票代码列表获得研报分析结果
        Arguments:
            end {str} -- 截止日期
        
        Keyword Arguments:
            start {str} -- 开始日期
            symbols {list} -- 股票代码列表
        """
        return self.call('get_stock_analysis', [end, start, symbols])

    def get_share_unlock(self, end, start, symbols=None, field=None):
        """根据开始和截止日期和股票列表和字段列表获得限售股解禁
        Arguments:
            start {str} -- 开始日期
            end {str} -- 截止日期

        Keyword Arguments:
            symbols {list of str} -- 股票列表
            field {list of str} -- 返回字段
        """
        return self.call('get_share_unlock', [end, start, symbols, field])
    
    def get_stock_business_info(self, symbols):
        """公司业务概要信息
        Arguments:
            symbols {list} -- 股票列表
        """
        return self.call('get_stock_business_info', [symbols])