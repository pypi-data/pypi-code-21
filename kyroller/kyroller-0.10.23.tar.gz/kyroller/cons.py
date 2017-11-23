import os
import ast


# 授权服务配置
AUTH_SERVER_ADDRESS = os.environ["AUTH_SERVER_ADDRESS"] if 'AUTH_SERVER_ADDRESS' in os.environ else 'https://auth.kuaiyutech.com/accessToken'

# 实时行情流地址 只有线上地址，不提供本地全推
REALTIME_QUOTATION_SERVER = os.environ["REALTIME_QUOTATION_SERVER"] if 'REALTIME_QUOTATION_SERVER' in os.environ else 'http://rt.kuaiyutech.com:12121'

# 回测行情流配置 默认线上地址，可以改为本地地址
ROLLBACK_QUOTATION_SERVER = os.environ["ROLLBACK_QUOTATION_SERVER"] if 'ROLLBACK_QUOTATION_SERVER' in os.environ else 'http://rk.kuaiyutech.com'


# 本地RPC 端口， 供 数据管理器用，界面管理
LOCAL_RPC_PORT = 12000
