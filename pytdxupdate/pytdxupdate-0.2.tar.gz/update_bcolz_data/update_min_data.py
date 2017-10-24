from update_bcolz_data.tdx_best_ip import select_best_ip,api
best_ip = select_best_ip()
from bcolz import ctable
import numpy as np
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
            for i in stock_list:
                th_pool.append(threading.Thread(target=merge_lastest_data,args=(api,path,i,fre,)))
                # merge_lastest_data(api,path,i,fre)
            for t in th_pool:
                t.start()
            for t in th_pool:
                t.join()
            # today = datetime.datetime.now().strftime('%Y-%m-%d')
            # print(today)
            # z = api.to_df(api.get_k_data('000001','2017-07-10',today))
            # print(z)

            # data = api.to_df(api.get_security_bars(8, 0, '000001', 0, 600))
            # ct = ctable(rootdir=bcolz_file_path + '000001' + '_' + '1m')
            # df = ct.todataframe()
            # last_time = df['kline_time'][-1:]
            # last_data = data[data['datetime'] >= pd.to_datetime(last_time.values[0]).strftime('%Y-%m-%d %H:%M')]
            # ct.trim(1)
            # for k,v in last_data.iterrows():
            #     ct.append(('000001',np.datetime64(v['datetime']+':00'),v['open']*100,v['high']*100,v['low']*100,v['close']*100,v['amount'],v['vol']))
            # ct.flush()


def merge_lastest_data(*args):
    api,path,stock,fre = args
    try:
        ct = ctable(rootdir=path + stock[0] + '_' + fre)
        df = ct.todataframe()
        data = api.to_df(api.get_security_bars(min_code[fre], stock[1], stock[0], 0, 800))
        last_time = df['kline_time'][-1:]
        last_data = data[data['datetime'] >= pd.to_datetime(last_time.values[0]).strftime('%Y-%m-%d %H:%M')]
        ct.trim(1)
        for k, v in last_data.iterrows():
            ct.append(('000001', np.datetime64(v['datetime'] + ':00'), v['open'] * 100, v['high'] * 100, v['low'] * 100,
                       v['close'] * 100, v['amount'], v['vol']))
        ct.flush()
    except Exception as e:
        print(stock)
        print(e)
    finally:
        pass


# merge_lastest_data(23432,[234,234])
# run()
# get_stock_list('/Users/apple/Work/dzh_project/bcolz_min_data/')