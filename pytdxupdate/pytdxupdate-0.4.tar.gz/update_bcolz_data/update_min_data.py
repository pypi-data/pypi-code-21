from update_bcolz_data.tdx_best_ip import select_best_ip,api
best_ip = select_best_ip()
from bcolz import ctable
import numpy as np
import math
import pandas as pd
from update_bcolz_data.stock_list import stock_list
min_code ={'5m':0,'15m':1,'30m':2,'60m':3,'1d':4,'1m':8}
import click,threading

@click.command()
@click.option('-p','--path_file')
@click.option('-f','--frequency')
def run(**options):
    path = options['path_file']
    fre = options['frequency']
    if path and fre in min_code.keys():
        th_pool = []
        with api.connect(best_ip, 7709):
            for x in range(math.ceil(len(stock_list)/800)):
                for i in stock_list[x*800:(x+1)*800]:
                    th_pool.append(threading.Thread(target=merge_lastest_data,args=(api,path,i,fre,)))
                    # merge_lastest_data(api,path,i,fre)
                for t in th_pool:
                    t.start()
                for t in th_pool:
                    t.join()

def merge_lastest_data(*args):
    api,path,stock,fre = args
    try:
        ct = ctable(rootdir=path + stock[0] + '_' + fre,mode='a')
        df = ct.todataframe()
        data = pd.concat([api.to_df(api.get_security_bars(min_code[fre], stock[1], stock[0], (9 - i) * 800, 800)) for i in range(10)],
                         axis=0)
        # data = api.to_df(api.get_security_bars(min_code[fre], stock[1], stock[0], 0, 800))
        last_time = df['kline_time'][-1:]
        last_data = data[data['datetime'] >= pd.to_datetime(last_time.values[0]).strftime('%Y-%m-%d %H:%M')]
        ct.trim(1)
        for k, v in last_data.iterrows():
            ct.append((stock[0], np.datetime64(v['datetime'] + ':00'), v['open'] * 100, v['high'] * 100, v['low'] * 100,
                       v['close'] * 100, v['amount'], v['vol']))
        ct.flush()
    except Exception as e:
        print(stock)
        print(e)
    finally:
        print('finished')


#--------test_code-------
# bcolz_file_path = '/Users/apple/Work/dzh_project/bcolz_min_data/'
# ct = ctable(rootdir=bcolz_file_path + '000001' + '_1m')
# ct = ct.todataframe()[:-1950]
# print(ct)
# with api.connect(best_ip, 7709):
#     data = pd.concat([api.to_df(api.get_security_bars(8, 0, '000001', (9 - i) * 800, 800)) for i in range(10)], axis=0)
#     ct = ctable(rootdir=bcolz_file_path + '000001' + '_1m',mode = 'a')
#     df = ct.todataframe()
#     # data = api.to_df(api.get_security_bars(min_code[fre], stock[1], stock[0], 0, 800))
#     last_time = df['kline_time'][-1:]
#     last_data = data[data['datetime'] >= pd.to_datetime(last_time.values[0]).strftime('%Y-%m-%d %H:%M')]
#     ct.trim(1)
#     for k, v in last_data.iterrows():
#         ct.append(('000001', np.datetime64(v['datetime'] + ':00'), v['open'] * 100, v['high'] * 100, v['low'] * 100,
#                    v['close'] * 100, v['amount'], v['vol']))
#     ct.flush()

    # data = data[data['datetime'] >= '2017-10-18 09:00']
    # print(data)
    # xx = open('log.txt',mode='w')
    #
    # for k, v in data.iterrows():
    #     xx.write(str( (np.datetime64(v['datetime'] + ':00'), v['open'] * 100, v['high'] * 100, v['low'] * 100,
    #                    v['close'] * 100, v['amount'], v['vol'])))
