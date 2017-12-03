import json, gzip, requests
import time, datetime

import math

from datalab.miscellaneous import clean_for_kairos
from datalab.src.loggers import datalab_loggers


datalab_logger_kairos_object = datalab_loggers.datalab_logger(my_format=datalab_loggers.DATALAB_LOGGER_FORMAT)
datalab_logger_kairos_inserters= datalab_logger_kairos_object.datalab_logger

def kairos_filter(data_point):
    """
    vltlogs and opslog kairos filter. Get only FPAR with numeric keyvalue
    :param data_point:
    :return:
    """
    try:
        x = float(data_point[9])
        if math.isnan(x) or math.isinf(x): return False
        return True
    except:
        return False



def kairos_insert(data, kairosdb_server, kairos_filter, kairos_parser):
    """
    Insert data in kairosdb_server that verify data_filter condition with structure data_parser

    :param data: list of datapoints to insert
    :param kairosdb_server: 'http://kairosdb_server:kairosdb_port'
    :data_filter: funcion of filter of a data point. Return true if point satisfy condicion
    :data_parser: Funcion to parse your data to insert in kairos. see kairos_parser
    :type data: list of list of the data or anything [][] accesible (ex: list of tubles)
    :type kairosdb_server: String
    :type data_filter: data_filter::data_point -> Boolean

    :return: tuple with kairos response object and number of data inserted
    """
    kairosdb_data=[]; n_data_inserted = 0;
    kairosdb_data = list(filter(kairos_filter, data))
    gzipped = gzip.compress(bytes(json.dumps(list(map(kairos_parser, kairosdb_data))), 'latin1'));
    headers = {'content-type': 'application/gzip'}
    response = requests.post(kairosdb_server + "/api/v1/datapoints", gzipped, headers=headers)
    datalab_logger_kairos_inserters.info("KAIROS : Inserted %d data : %d (status code)" % (len(kairosdb_data) if response.status_code == 204 else 0, response.status_code))
    n_data_inserted = len(kairosdb_data) if response.status_code == 204 else 0
    return (response, n_data_inserted)


def kairos_parser(data_point):
    """
    Kairos datalab basic parser

    :param data_point: your data point
    :type data_point: tuple, list etc of values
    :return: dictionary of your datapoint parsed
    :rtype: diccionary
    """
    data_point_parsed = {
        "name": clean_for_kairos(data_point[8]),
        "timestamp":int(time.mktime(data_point[1].timetuple()))*1000, #kairosdb time in miliseconds
        "value"    : float(data_point[9]),
        "tags": {
             "proc": clean_for_kairos(data_point[4]),
             "env": clean_for_kairos(data_point[3]),
             "loghost": clean_for_kairos(data_point[2]),
             "logtext": clean_for_kairos(str(data_point[10]).replace(" ", "_")),
        }
    }
    return data_point_parsed


def kairos_keep_alive(kairosdb_server, metric):
    """
    Utility funcion. Writi in kairos a data with the metric pased and keyvalue 1
    :param kairosdb_server:
    :param metric: name of the metric
    :return:
    """
    keep_alive = [(time.mktime(datetime.datetime.now().timetuple()),datetime.datetime.now(),'datalab','datalab','datalab',0,'','FPAR',metric,'1','Mensaje de keep alive','',0,'','')]
    gzipped = gzip.compress(bytes(json.dumps(list(map(kairos_parser,keep_alive))), 'latin1'))
    headers = {'content-type': 'application/gzip'}
    response = requests.post(kairosdb_server + "/api/v1/datapoints", gzipped, headers=headers)
    return response

if __name__ == "__main__":
    pass;