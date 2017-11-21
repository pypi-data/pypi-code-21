# -*- coding:utf-8 –*-
from os.path import join
from tdx import TDX_ROOT

# 自定义板块目录，需要由通达信客户端导出
CUSTOMER_BLOCK_PATH = join(TDX_ROOT,'data/blocknew')

# 股本变迁文件，内容包含除息除权，以及股本变动数据，在客户端安装目录
GBBQ_PATH = join(TDX_ROOT,'data/gbbq')