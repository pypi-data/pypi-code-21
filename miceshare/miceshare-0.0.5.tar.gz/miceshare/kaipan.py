# coding: utf-8

import requests
import time
import json
import traceback
import datetime
import sys
import pandas as pd

'''
转换数字股票代码id,600136.XSHG->600136
'''


def get_stock_code(stock_code):
    code = stock_code
    idx = stock_code.find('.')
    if idx > 0:
        code = code[0:idx]
    return code


# 资金流计算
'''=============================================东财数据获取========================================================'''


# 参考地址 http://liam0205.me/2016/02/27/The-requests-library-in-Python/
def http_get_em(url, params):
    my_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
        'Content-Type': 'application/x-www-form-urlencoded'}
    try:
        r = requests.get(url, headers=my_headers, data=params, timeout=5)
        #         print(r.status_code, r.reason,r.text)
        return r.text
    except:
        return 'http get exception'


'''
get content between str1 and str2 in str
'''


def str_get_between(str, str1, str2):
    strOutput = str[str.find(str1) + len(str1):str.find(str2)]
    return strOutput


'''
转换成东财的股票代码id,600136.XSHG->6001361
'''


def get_stock_id_eastmoney(stock_code):
    code = stock_code
    idx = stock_code.find('.')
    if idx > 0:
        code = code[0:idx]
    if code.startswith("60"):
        code = code + "1";
    elif code.startswith("00"):
        code = code + "2";
    elif code.startswith("300"):
        code = code + "2";
    # print(code)
    return code


'''
聚宽的id
'''


def get_stock_id_jq(stock_code):
    code = stock_code
    idx = stock_code.find('.')
    if idx > 0:
        code = code[0:idx]
    if code.startswith("60"):
        code = code + ".XSHG";
    elif code.startswith("00"):
        code = code + ".XSHE";
    elif code.startswith("300"):
        code = code + ".XSHE";
    # print(code)
    return code


'''
http://ff.eastmoney.com/EM_CapitalFlowInterface/api/js?id=6003261&type=ff&check=MLBMS&cb=var%20aff_data=&js={(x)}&rtntype=3&_=1493254730313
每分钟的数据，按照下面的顺序的数组，比如：'-1232.0203,-456.3307,-775.6896,157.0809,1074.939'
今日主力净流入：-1232.0200万元,主力净比：-1.25%
今日超大单净流入：-456.3300万元,超大单净比：-0.46%
今日大单净流入：-775.6900万元,大单净比：-0.79%
今日中单净流入：157.0800万元,中单净比：0.16%
今日小单净流入：1074.9400万元,小单净比：1.09%
'''


def parse_money_flow_minute_now(stock):
    now = str(time.time())
    stock = get_stock_id_eastmoney(stock)
    url = 'http://ff.eastmoney.com/EM_CapitalFlowInterface/api/js?id=' + stock + '&type=ff&check=MLBMS&cb=var%20aff_data=&js={(x)}&rtntype=3&acces_token=1942f5da9b46b069953c873404aad4b5&_=' + now
    #    print(url)
    html = http_get_em(url, '')
    data = str_get_between(html, '"ya":', '}')
    #     print(data)
    data = json.loads(data)
    #     print(data)
    return data


'''
获取资金流-历史-天拆分
'''


def get_money_flow_day(stock, date):
    mf = jqdata.get_money_flow(stock, end_date=date, count=1)
    #     print(mf)
    #     print(mf.net_amount_xl+mf.net_amount_l)
    return mf.net_amount_xl + mf.net_amount_l


'''=============================================kaipan数据获取========================================================'''
'''
开盘的数据获取，整理接口：
获取资金流-历史
获取资金流-当天实时
获取分钟K线-当天实时
获取盘口-当天实时

注意：使用自己账户信息获取数据
'''


class KaipanData():
    def __init__(self):
        pass

    g_token = '86402db4dedc31239b54eb6763b57d47'  # 有些需要权限的需要抓手机得到
    g_url_now = 'https://hq.kaipanla.com/w1/api/index.php'  # 实时接口
    g_url_his = 'https://his.kaipanla.com/w1/api/index.php'  # 历史接口
    # 统一模拟请求头
    my_headers = {'Content-type': 'multipart/form-data; boundary=xds~Boundary',
                  'Accept': '/',
                  'Content-Length': '536',
                  'User-Agent': '%E5%BC%80%E7%9B%98%E5%95%A6/6 CFNetwork/808.2.16 Darwin/16.3.0',
                  'Accept-Language': 'zh-cn',
                  'Accept-Encoding': 'gzip, deflate'
                  }
    my_headers_his = {'Host': 'his.kaipanla.com'}
    my_headers_his.update(my_headers)
    my_headers_now = {'Host': 'hq.kaipanla.com'}
    my_headers_now.update(my_headers)

    '''
    转换数字股票代码id,600136.XSHG->600136
    '''

    def get_stock_code(self, stock_code):
        code = stock_code
        idx = stock_code.find('.')
        if idx > 0:
            code = code[0:idx]
        return code

    '''
    统一请求
    '''

    def post(self, url, headers, body, attr=None, timeout=5):
        # body的另外一种方式，待尝试，简化代码
        #     files={"UserID":(None,'103935'),"a":(None,"GetStockChouMa"),"Token":(None,"f5f65817cf08a406918ea918690d18ea"),
        # "c":(None,"StockL2History"),"StockID":(None,stock),"Day":(None,date),"apiv":(None,"w4")}
        try:
            r = requests.post(url, headers=headers, data=body, timeout=timeout)
            if (r.status_code == 200):
                rs_josn = r.json()
                if None != attr:
                    return rs_josn[attr]
                else:
                    return rs_josn
        except Exception as e:
            print("longge http post exception ", e)
            return []

    '''获取资金流数据-历史
    [-49708600, 18441100, 3754260, 27513200, 14, 19104200, 264, 1183620000, '15:00']
    大于50万，30-50万，10-30万，小于10万，对倒次数，对待金额，异动次数，成交额，时间
    '''

    def get_money_flow_m5_hist_kaipan(self, stock, date):
        body = """\
--xds~Boundary
Content-Disposition: form-data; name="a"

GetStockChouMa
--xds~Boundary
Content-Disposition: form-data; name="c"

StockL2History
--xds~Boundary
Content-Disposition: form-data; name="StockID"

%s
--xds~Boundary
Content-Disposition: form-data; name="UserID"

103935
--xds~Boundary
Content-Disposition: form-data; name="Token"

%s
--xds~Boundary
Content-Disposition: form-data; name="Day"

%s
--xds~Boundary
Content-Disposition: form-data; name="apiv"

w4

""" % (stock, self.g_token, date)
        return self.post(self.g_url_his, self.my_headers_his, body, attr='List')

    '''
    获取资金流数据-当天-5分钟拆分，每分钟更新一次数据，不够的计入当前
    stock : "002350"
    [-49708600, 18441100, 3754260, 27513200, 14, 19104200, 264, 1183620000, '15:00']
    大于50万，30-50万，10-30万，小于10万，对倒次数，对待金额，异动次数，成交额，时间
    '''

    def get_money_flow_m5_now_kaipan(self, stock):
        stock = self.get_stock_code(stock)
        body = """\
--xds~Boundary
Content-Disposition: form-data; name="UserID"

103935
--xds~Boundary
Content-Disposition: form-data; name="a"

StockChouMaByTimeNew
--xds~Boundary
Content-Disposition: form-data; name="Token"

%s
--xds~Boundary
Content-Disposition: form-data; name="c"

StockYiDongKanPan
--xds~Boundary
Content-Disposition: form-data; name="StockID"

%s
""" % (self.g_token, stock)
        return self.post(self.g_url_now, self.my_headers_now, body, attr='List')

    '''
    获取今天的最新5分钟主力资金流数据=特大单+大单
    '''

    def get_money_flow_m5_kaipan(self, stock, default_value=0):
        try:
            mm_m5 = self.get_money_flow_m5_now_kaipan(stock)
            for i in range(-1, -len(mm_m5), -1):
                c_mm = mm_m5[i]
                print(c_mm)
                large_mf = c_mm[0] + c_mm[1]
                if large_mf != 0:
                    return round(large_mf / 10000, 2)
            return 0
        except:
            print("get_money_flow_m5_kaipan exception ", traceback.print_exc())
            return default_value

    '''
    分钟K线图，返回数据如下：
    {
        "trend": [
            ["09:30", 32.35, 32.3716, 3032, 2],
            ["09:31", 32.27, 32.3475, 1804, 0],
            ["09:32", 32.23, 32.3119, 2594, 0],
            ...
            ["15:00", 32.47, 32.4896, 12, 2]
        ],
        "hprice": 32.74,
        "lprice": 32.22,
        "preclose_px": 32.45,
        "day": "20170922",
        "time": "1506063702",
        "code": "600340",
        "errcode": 0
    }
    '''

    def get_stock_trend_m1_now_kaipan(self, stock):
        stock = self.get_stock_code(stock)
        body = """\
--xds~Boundary
Content-Disposition: form-data; name="a"

GetStockTrend
--xds~Boundary
Content-Disposition: form-data; name="c"

StockL2Data
--xds~Boundary
Content-Disposition: form-data; name="StockID"

%s
--xds~Boundary
Content-Disposition: form-data; name="UserID"

103935
--xds~Boundary
Content-Disposition: form-data; name="DeviceID"

0f1ac73919caf7c55ecf23ffe6624d2d344faeae
--xds~Boundary
Content-Disposition: form-data; name="Token"

%s
--xds~Boundary
Content-Disposition: form-data; name="apiv"

w4
""" % (stock, self.g_token)
        return self.post(self.g_url_now, self.my_headers_now, body)

    '''
    盘口数据，返回结果如下
    {
        "day": 20170922,
        "code": "600340",
        "name": "\u534e\u590f\u5e78\u798f",
        "preclose_px": 32.45,#昨天收盘价
        "status": 86,
        "real": {
            "time": 150001000,
            "last_px": 32.47,#当前价
            "px_change": 0.02,#当前价格变动
            "px_change_rate": 0.06,#当前价格变动幅度
            "high_px": 32.74,#最高价
            "low_px": 32.22,#最低价
            "open_px": 32.36,#开盘价
            "avg_px": 32.4896,#均价
            "turnover_ratio": "0.66",#换手率
            "total_amount": 195363,#成交量总手
            "total_turnover": 634727980,#成交量总金额
            "vol_ratio": 0.49,#量比
            "up_px": 35.7,#涨停价
            "down_px": 29.21,#跌停价
            "amplitude": 1.6,#振幅
            "entrust_rate": -41.1,#委比
            "amount_in": 117837,#内盘
            "amount_out": 77525,#外盘
            "pe_rate": 8.94,#市盈率
            "dyn_pb_rate": 3.62,#市净率
            "circulation_amount": 2954946709,#流通股本
            "circulation_value": 95947112448,#流通市值
            "total_shares": 2954946709,#流通股本
            "market_value": 95947112448,#流通市值
            "actualcirculation_value": 40671980966#实际市值
        },
        "weituo": {
            "totals": 45940,
            "avg_askpx": 33.697,
            "s10": [0, 0],
            "s9": [0, 0],
            "s8": [0, 0],
            "s7": [0, 0],
            "s6": [0, 0],
            "s5": [32.52, 58],
            "s4": [32.51, 104],
            "s3": [32.5, 234],
            "s2": [32.49, 165],
            "s1": [32.48, 175],
            "totalb": 19175,
            "avg_bidpx": 31.96,
            "b1": [32.47, 25],
            "b2": [32.46, 31],
            "b3": [32.45, 405],
            "b4": [32.44, 78],
            "b5": [32.43, 159],
            "b6": [0, 0],
            "b7": [0, 0],
            "b8": [0, 0],
            "b9": [0, 0],
            "b10": [0, 0]
        },
        "errcode": 0,
        "ICon": 1,
        "Gang": ""
    }
    '''

    def get_stock_pankou_now_kaipan(self, stock):
        stock = self.get_stock_code(stock)
        body = """\
--xds~Boundary
Content-Disposition: form-data; name="a"

GetStockPanKou
--xds~Boundary
Content-Disposition: form-data; name="c"

StockL2Data
--xds~Boundary
Content-Disposition: form-data; name="StockID"

%s
--xds~Boundary
Content-Disposition: form-data; name="UserID"

103935
--xds~Boundary
Content-Disposition: form-data; name="DeviceID"

0f1ac73919caf7c55ecf23ffe6624d2d344faeae
--xds~Boundary
Content-Disposition: form-data; name="Token"

%s
--xds~Boundary
Content-Disposition: form-data; name="apiv"

w4

""" % (stock, self.g_token)
        return self.post(self.g_url_now, self.my_headers_now, body)

    '''
    获取日K数据
    "x": ["20151210", "20151211", ...] 日期
    "y": [
            [7.07, 8.37, 8.37, 7.07],#价格数据
            ...
            开盘，收盘，最高，最低
            [43.3, 42.58, 43.98, 42.27],
        ]
    "vol": [93, 43...
    "turnover": [0.04, 0.02,...
    '''

    def get_stock_kline_his_kaipan(self, stock):
        url = 'https://his.kaipanla.com/w1/api/index.php?apiv=w4'
        headers = {'Host': 'his.kaipanla.com',
                   'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                   'Origin': 'https://page.kaipanla.com',
                   'Accept-Encoding': 'gzip, deflate',
                   'Connection': 'keep-alive',
                   'Accept': 'application/json, text/javascript, */*; q=0.01',
                   'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Mobile/14G60',
                   'Referer': 'https://page.kaipanla.com/w4/web/StockDetails4_ios.html?SID=%s' % (stock),
                   'Accept-Language': 'zh-cn'
                   }
        stock = self.get_stock_code(stock)
        body = "StockID=%s&Type=d&Index=0&st=400&c=StockLineData&a=GetKLineDay&UserID=103935&Token=%s" % (stock, self.g_token)
        return self.post(url, headers, body)

    '''
    获取市场风口-板块数据
    date 格式：20171009
    is_hist：历史数据则设置为True否则获取到最新数据，不管date参数
    返回数据：
        [
            ["\u533b\u7597\u6539\u9769", "2100"], #板块名称，计算指数
            ["\u6b21\u65b0\u80a1", "488.42"],
            ......
        ]
    '''

    def get_market_fire_board_kaipan(self, date, is_his=False):
        if is_his:
            url = 'https://his.kaipanla.com/w1/api/index.php?apiv=w4'
            headers = {'Host': 'his.kaipanla.com',
                       'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                       'Origin': 'https://page.kaipanla.com',
                       'Accept-Encoding': 'gzip, deflate',
                       'Connection': 'keep-alive',
                       'Accept': 'application/json, text/javascript, */*; q=0.01',
                       'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Mobile/14G60',
                       'Referer': 'https://page.kaipanla.com/w4/web/capitalSpYD_ios.html',
                       'Accept-Language': 'zh-cn'
                       }
            body = "c=StockFengKData&a=GetFengKYDPlate&Day=%s&UserID=103935&Token=%s" % (date, self.g_token)
            return self.post(url, headers, body, attr='List')
        else:
            url = 'https://hq.kaipanla.com/w1/api/index.php?apiv=w4'
            headers = {'Host': 'hq.kaipanla.com',
                       'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                       'Origin': 'https://page.kaipanla.com',
                       'Accept-Encoding': 'gzip, deflate',
                       'Connection': 'keep-alive',
                       'Accept': 'application/json, text/javascript, */*; q=0.01',
                       'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Mobile/14G60',
                       'Referer': 'https://page.kaipanla.com/w4/web/capitalSpYD_ios.html',
                       'Accept-Language': 'zh-cn'
                       }
            body = "c=StockFengKData&a=GetFengKYDPlate&UserID=103935&Token=%s" % (self.g_token)
            return self.post(url, headers, body, attr='List')

    '''
    根据风口板块获取风口股票数据
    date 格式：20171009
    is_hist：历史数据则设置为True否则获取到最新数据，不管date参数
    返回数据格式：
        [{
            "StockID": "002223", #代码
            "StockName": "\u9c7c\u8dc3\u533b\u7597", #名称
            "jiage": "22.9600", #价格
            "zhangfu": "10.01%", #涨幅
            "sjltp": 13525339080, #实际流通市值
            "ZJBuy": 161131150, #主力买入
            "ZJSell": 105667318, #主力卖出
            "ZJJE": 55463832,#主力净额
            "GN": "\u533b\u7597\u6539\u9769", #板块
            "GN2": "\u533b\u7597\u6539\u9769", #板块
            "gang": "",
            "ZTState": 1,
            "ZTTime": "1507618674"}
            ...
            ]
    '''

    def get_market_fire_stock_of_board_kaipan(self, board, date, is_his=False):
        if is_his:
            url = 'https://his.kaipanla.com/w1/api/index.php?apiv=w4'
            headers = {'Host': 'his.kaipanla.com',
                       'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                       'Origin': 'https://page.kaipanla.com',
                       'Accept-Encoding': 'gzip, deflate',
                       'Connection': 'keep-alive',
                       'Accept': 'application/json, text/javascript, */*; q=0.01',
                       'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Mobile/14G60',
                       'Referer': 'https://page.kaipanla.com/w4/web/capitalSpGN_ios.html?n=%s&date=%s' % (board, date),
                       'Accept-Language': 'zh-cn'
                       }
            body = "c=StockFengKData&a=GetFengKYDPlateInfo&Plate=%s&filter=0&Jump=1&Day=%s&UserID=103935&Token=%s" % (board, date, self.g_token)
            return self.post(url, headers, body, attr='List')
        else:
            url = 'https://hq.kaipanla.com/w1/api/index.php?apiv=w4'
            headers = {'Host': 'hq.kaipanla.com',
                       'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                       'Origin': 'https://page.kaipanla.com',
                       'Accept-Encoding': 'gzip, deflate',
                       'Connection': 'keep-alive',
                       'Accept': 'application/json, text/javascript, */*; q=0.01',
                       'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Mobile/14G60',
                       'Referer': 'https://page.kaipanla.com/w4/web/capitalSpGN_ios.html?n=%s' % (board),
                       'Accept-Language': 'zh-cn'
                       }
            body = "c=StockFengKData&a=GetFengKYDPlateInfo&Plate=%s&filter=0&Jump=1&UserID=103935&Token=%s" % (board, self.g_token)
            return self.post(url, headers, body, attr='List')

    '''
    委卖委买数据
    {
        "bsentrust": [
            [
                "09:30",
                3500,
                12526,
                10440500,
                39746696
            ],
            [
                "09:31",
                6057,
                15429,
                18075904,
                48897448
            ],
            ...
        ],
        "maxentrust": 39146,
        "minentrust": 3500,
        "minentrustdiff": -21267,
        "maxentrustdiff": -1614,
        "maxturnover": 123139824,
        "mineturnover": 10440500,
        "mineturnoverdiff": -69024772,
        "maxturnoverdiff": -9686296,
        "day": "20171110",
        "time": "1510470100",
        "code": "600340",
        "errcode": 0,
        "time2": 1510476870
    }
    '''
    def get_bs(self, code):
        stock = self.get_stock_code(code)
        data = {'c': 'StockL2Data', 'a': 'GetStockBsvolume', 'apiv': 'w5'}
        data['StockID'] = stock
        url = "http://hq.kaipanla.com/w1/api/index.php"
        headers = {"User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.0; BLN-AL10 Build/HONORBLN-AL10)",
                   "Host": "hq.kaipanla.com"
                   }
        post = requests.post(url, data=data, headers=headers)
        if post.status_code == 200:
            return post.text
        print('get bs fail', post.status_code)
        return None


    def get_bs_df(self, code):
        json = get_bs(code)
        if json:
            ret = json['bsentrust']
            df = pd.DataFrame(ret)
            return df
        print('not found')
        return None


# 为了兼容直接暴露以下方法
kaipan_data = KaipanData()

# 委卖委买数据
def get_bs(stock):
    return kaipan_data.get_bs(stock)

# 今天分钟K线明细
def get_stock_trend_m1_now_kaipan(stock):
    return kaipan_data.get_stock_trend_m1_now_kaipan(stock)


# 今天所有资金流数据明细
def get_money_flow_m5_now_kaipan(stock):
    return kaipan_data.get_money_flow_m5_now_kaipan(stock)


# 今天最新数据主力资金
def get_money_flow_m5_kaipan(stock):
    return kaipan_data.get_money_flow_m5_kaipan(stock)


# 历史某天的资金流数据明细
def get_money_flow_m5_hist_kaipan(stock, date):
    return kaipan_data.get_money_flow_m5_hist_kaipan(stock, date)


# 今天的盘口数据
def get_stock_pankou_now_kaipan(stock):
    return kaipan_data.get_stock_pankou_now_kaipan(stock)


def get_stock_kline_his_kaipan(stock):
    return kaipan_data.get_stock_kline_his_kaipan(stock)


# 板块风口排名数据
def get_market_fire_board_kaipan(date, is_his=False):
    return kaipan_data.get_market_fire_board_kaipan(date, is_his)


# 根据风口板块获取对应的股票
def get_market_fire_stock_of_board_kaipan(board, date, is_his=False):
    return kaipan_data.get_market_fire_stock_of_board_kaipan(board, date, is_his)


if __name__ == "__main__":
    '''测试'''
    stock = "600340"
    # mf = get_stock_trend_m1_now_kaipan(stock)
    # print(mf)

    # mf = get_money_flow_m5_kaipan(stock)
    # print(mf)

    # mf = get_money_flow_m5_now_kaipan(stock)
    # print(mf)

    # mf = get_money_flow_m5_hist_kaipan(stock,"2017005")
    # print(mf)

    # mf = get_stock_pankou_now_kaipan(stock)
    # print(mf)

    # mf = get_stock_kline_his_kaipan(stock)
    # print(mf)

    # mf = get_market_fire_board_kaipan('20171010')
    # print(mf)

    # mf = get_market_fire_stock_of_board_kaipan('5G', '20171010', is_his=False)
    mf = get_bs(stock)
    print(mf)

