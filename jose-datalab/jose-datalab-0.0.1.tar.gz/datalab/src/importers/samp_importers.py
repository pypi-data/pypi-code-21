import datetime, time
import math

import functools
import requests, json, gzip
import linecache

import pandas as pd



def _samp_kairos_parser(keyname, tags, tsp_kv):
    """

    :param keyname:
    :param tags:
    :param tsp_kv:
    :return:
    """
    t=datetime.datetime.strptime(str(tsp_kv[0])+str(tsp_kv[1]),"%Y-%m-%d%H:%M:%S.%f")
    data_point_parsed = {
        "name": keyname,
        "timestamp": int(time.mktime(t.timetuple()))*1000 + int(t.microsecond/1000), #kairosdb time in miliseconds
        "value"    : float(tsp_kv[2]),
        "tags": tags
    }
    return data_point_parsed


def _samp_kairos_clean(x):
    """

    :param x:
    :return:
    """
    try:
        y = float(x[2])
        if math.isnan(y) or math.isinf(y):
            return False
        datetime.datetime.strptime(str(x[0])+str(x[1]), "%Y-%m-%d%H:%M:%S.%f")
        return True
    except:
        return False

def _samp_kairos_insert(kairosdb_server, keyname, tsp_kv, tags):
    """

    :param kairosdb_server:
    :param keyname:
    :param tsp_kv:
    :param tags:
    :return:
    """
    kairosdb_data=[]; n_data_inserted = 0;
    kairosdb_data = list(filter(_samp_kairos_clean, tsp_kv))
    f = functools.partial(_samp_kairos_parser, keyname, tags)
    gzipped = gzip.compress(bytes(json.dumps(list(map(f, kairosdb_data))), 'latin1'));
    headers = {'content-type': 'application/gzip'}
    response = requests.post(kairosdb_server + "/api/v1/datapoints", gzipped, headers=headers)
    #datalab_logger_inserted.info("KAIROS : Inserted %d data : %d (status code)" % response.status_code)
    n_data_inserted = len(kairosdb_data) if response.status_code == 204 else 0
    #datalab_logger_inserted.info("KAIROS : Error inserting data")
    return (response, n_data_inserted)

def samp_import(path_to_samp,kairos_server):
    """

    :param path_to_samp:
    :param kairos_server:
    :return:
    """
    chunksize=10000
    env = linecache.getline(path_to_samp, 3).split(' ')[2][1:-1].replace(":", "")
    tags = {'env':env}
    l = linecache.getline(path_to_samp, 5)
    ls = l.split(' ');
    attributes=int(ls[4]) #N of atributes
    keyvnames = ['Record Index', 'Time Sequence', 'yyyy-mm-dd', 'hh:mm:ss.uuuu']
    for i in range(0,attributes): # We get the keyvnames
        l = linecache.getline(path_to_samp, 14+i)
        keyvname = (" ".join(l.split()).split())[2].replace(":", ".").replace("\"", "")
        if keyvname[0] == '.': keyvname=keyvname[1:]
        keyvnames.append(keyvname)
    headers_rows=range(1,13+attributes+9)
    df = pd.read_csv(filepath_or_buffer=path_to_samp, names=keyvnames, na_values=[""], skiprows=headers_rows, delim_whitespace=True, chunksize=chunksize)
    for chunk in df:
        for i in range(1, attributes + 1):
            kairos_result=_samp_kairos_insert(kairos_server, keyvnames[3+i], chunk[['yyyy-mm-dd', 'hh:mm:ss.uuuu', keyvnames[3+i]]].values, tags) #We Insert Timestamp-Keyvalues
    if "#___oOo___" in str(chunk[['Record Index']][-1:]):
        print("End of File reach")
    else:
        print("Onlyne file")



def _g(x,y):
    return x<y

UPDATETIME=100
def samp_online_import(path_to_samp,kairos_server):
    """

    :param path_to_samp:
    :param kairos_server:
    :return:
    """
    chunksize=10000
    env = linecache.getline(path_to_samp, 3).split(' ')[2][1:-1].replace(":", "")
    tags = {'env':env}
    l = linecache.getline(path_to_samp, 5)
    ls = l.split(' ');
    attributes=int(ls[4]) #N of atributes
    keyvnames = ['Record Index', 'Time Sequence', 'yyyy-mm-dd', 'hh:mm:ss.uuuu']
    for i in range(0,attributes): # We get the keyvnames
        l = linecache.getline(path_to_samp, 14+i)
        keyvname = (" ".join(l.split()).split())[2].replace(":", ".").replace("\"", "")
        if keyvname[0] == '.': keyvname=keyvname[1:]
        keyvnames.append(keyvname)
    header_lines=13+attributes+9
    f = functools.partial(_g, x=header_lines)
    while True:
        df = pd.read_csv(filepath_or_buffer=path_to_samp, names=keyvnames, na_values=[""], skiprows=f, delim_whitespace=True, chunksize=chunksize,)
        for chunk in df:
            for i in range(1, attributes + 1):
                kairos_result=_samp_kairos_insert(kairos_server, keyvnames[3+i], chunk[['yyyy-mm-dd', 'hh:mm:ss.uuuu', keyvnames[3+i]]].values, tags) #We Insert Timestamp-Keyvalues
        if "#___oOo___" in str(chunk[['Record Index']][-1:]):
            print("End of File reach")
            break
        else:
            print("Onlyne file")
            x=int(chunk[['Record Index']].iloc[-1])
            f = functools.partial(_g,x=header_lines+x)
            time.sleep(UPDATETIME)

if __name__ == "__main__":
    pass;


