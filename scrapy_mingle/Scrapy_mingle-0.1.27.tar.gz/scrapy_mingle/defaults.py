import redis
from scrapy_mingle.proxy_getter import get_proxy

# ----------- for redis setting ---------------

REDIS_CLS = redis.StrictRedis
REDIS_ENCODING = 'utf-8'
# Sane connection defaults.
REDIS_PARAMS = {
    'socket_timeout': 30,
    'socket_connect_timeout': 30,
    'retry_on_timeout': True,
    'encoding': REDIS_ENCODING,
}


# ----------- for proxy middleware setting ---------------
# 代理文件位置
PROXYFILE = 'proxy.json'
# 更新代理频率
UPDATE_FREQ = 1800
# 代理最小更新周期（代理更新频率太快，会导致获取不到新代理，浪费效率）
UPDATE_INV = 120
# 阈值，可用代理数小于这个值时获取新代理
PROXY_THRESHOLD = 15
# 代理抓取程序
PROXY_GETTER = get_proxy
# 被反爬出现的status_code
BAN_CODE = set((302, 403))
IGNORE_CODE = set([404])

PROXY_URL = ''
