import requests
import datetime, time
import pandas as pd
import json

def convertHumanTime2kairosTime(s):
    t=datetime.datetime.strptime(str(s),"%Y-%m-%d %H:%M:%S.%f")
    return int(time.mktime(t.timetuple()))*1000 + int(t.microsecond/1000)

def _getkw(server, old, new, metric):
    query = {
        "metrics": [
        {
            "tags": {},
            "name": metric,
            "aggregators": [
            {
                "name": "sum",
                "align_sampling": True,
                "sampling": {
                    "value": "1",
                    "unit": "milliseconds"
                },
            "align_start_time": False
            }]
        }],
        "cache_time": 0,
        "start_absolute": convertHumanTime2kairosTime(old),
        "end_absolute": convertHumanTime2kairosTime(new)
     }
    response = requests.post(server + "/api/v1/datapoints/query", data=json.dumps(query))
    return response.json()["queries"][0]['results'][0]['values']


def get_kairos_data(server, old, new, metric):
    return [x[1] for x in _getkw(server, old, new, metric)]

def get_kairos_timestamp(server, old, new, metric):
    return [x[0] for x in _getkw(server, old, new, metric)]


server = "http://134.171.189.10:8080"
metric = "INS.AO.SENS1.VAL1"

from_ = "2017-08-01 22:22:22.003"
to = "2017-08-01 22:25:22.003"

def getkw(server, old, new, metrics):
    merge = pd.Series(get_kairos_data(server, old, new, metrics[0]), index=pd.to_datetime(get_kairos_timestamp(server, old, new, metrics[0]), unit='ms'))
    for metric in metrics[1:]:
        serie = pd.Series(get_kairos_data(server, old, new, metric), index=pd.to_datetime(get_kairos_timestamp(server, old, new, metric), unit='ms'))
        merge = pd.concat([merge, serie], axis=1)
    return merge.resample('10s').mean().interpolate(method='nearest').fillna(method='pad').fillna(method='bfill')




