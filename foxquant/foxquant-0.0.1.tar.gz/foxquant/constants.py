# coding=utf-8

INDEX_SH = 'IDX.000001'  # 上证指数
INDEX_SZ = 'IDX.399001'  # 深证成指
INDEX_CY = 'IDX.399006'  # 创业板指
INDEX_SH50 = 'IDX.000016'  # 上证50
INDEX_HS300 = 'IDX.000300'  # 沪深300

INDEXS = [INDEX_SH, INDEX_SZ, INDEX_CY, INDEX_SH50, INDEX_HS300]
INDEX_NAMES = ['上证指数', '深证成指', '创业板指', '上证50', '沪深300']

DATA_SERVER_URL = 'http://fox.cainiaotouzi.cn/api'

TODAY_QUOTE_FILE = DATA_SERVER_URL + '/today/quote'
TODAY_MONEY_FILE = DATA_SERVER_URL + '/today/money'
