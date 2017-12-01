import multiprocessing
import os, time
import glob

import math
import pandas as pd
import xxhash
import functools

from elasticsearch import ConnectionTimeout
from elasticsearch.helpers import streaming_bulk

from datalab import miscellaneous
from datalab.miscellaneous import clean_for_kairos
from datalab.src.connections.connections import es_connection_setUp
from datalab.src.importers.es_impoters import ES_BASIC_INDEXES, ES_BASIC_INDEXES_FILTERS, ES_BASIC_DOC_TYPES, \
    ES_BASIC_DOC_TYPES_FILTERS, ES_VLTLOG_OPSLOG_GENERATORS_DATA, es_insert_2, _get_index_with_suffix_name, \
    datalab_logger_es_inserters
from datalab.src.importers.kairos_importers import kairos_insert
from datalab.src.loggers import datalab_loggers




datalab_logger_csvImporters_object = datalab_loggers.datalab_logger(my_format=datalab_loggers.DATALAB_LOGGER_FORMAT)
datalab_logger_csvInserters = datalab_logger_csvImporters_object.datalab_logger

def csv_opslog_filter(data_point):
    if data_point[0].lower() == 'fpar':
        try:
            x = float(data_point[8])
            if math.isnan(x) or math.isinf(x): return False
            return True
        except:
            return False
    else:
        return False


def csv_kairos_parser(data_point):
    data_point_parsed = {
        "name": clean_for_kairos(data_point[7]),
        "timestamp": int(time.mktime(time.strptime(str(data_point[1]), "%Y-%m-%d %H:%M:%S"))) * 1000,
        # kairosdb time in miliseconds
        "value": float(data_point[8]),
        "tags": {
            "proc": clean_for_kairos(data_point[4]),
            "env": clean_for_kairos(data_point[3]),
            "logh4pysost": clean_for_kairos(data_point[2]),
            "logtext": clean_for_kairos(str(data_point[9]).replace(" ", "_")),
        }
    }
    return data_point_parsed


CSV_VLTLOG_OPSLOG_HEADER = ['typelog', 'tm', 'loghost', 'env', 'procname', 'procid', 'module', 'keyw', 'keyv',
                            'logtext', 'errstack', 'errstackidx', 'errlocation', 'errseverity']


def csv_kairos_import(path_to_csv, kairos_server="http://192.168.1.10:8080", header=CSV_VLTLOG_OPSLOG_HEADER,
                      csv_filter=csv_opslog_filter, kairos_parser=csv_kairos_parser):
    chunksize = 50000
    df = pd.read_csv(filepath_or_buffer=path_to_csv, names=header, compression='gzip', na_values=[""],
                     parse_dates=['tm'], engine='c', encoding='latin-1', usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                     na_filter=False, chunksize=chunksize)
    pool = multiprocessing.Pool(4)
    for chunk in df:
        r = pool.apply_async(kairos_insert,
                             args=[chunk.values, kairos_server, csv_filter, kairos_parser])  # ,callback=callBack)
        # result.append(r.get()) #RECOJER LOS RESULTADOS RALENTIZA X4
    pool.close()
    pool.join()
    return r.get()  # DEVOLVEMOS SOLO EL ULTIMO RESULTADO POR MOTIVOS DE VELOCIDAD. CON ESTE SE PUEDE DEDUCIR SI LA INSERCION FUE BIEN


def csv_es_opslog_generator_data(data,index, doc_type):
    for data_point in data:
        yield {
            '_index': index,
            '_type': doc_type,
            '_id': xxhash.xxh64(str(data_point[10])+str(data_point[11])+str(data_point[12])+str(data_point[13])).hexdigest()+xxhash.xxh64(str(data_point[1])+str(data_point[0])+str(data_point[2])+str(data_point[3])+str(data_point[4])+str(data_point[5])+str(data_point[6])+str(data_point[7])+str(data_point[8])+str(data_point[9])).hexdigest(),
            '_source':  {
                          '@timestamp': data_point[1],
                          'loghost': data_point[2] ,
                          'envname': data_point[3],
                          'procname':data_point[4],
                          'procid':data_point[5],
                          'module':data_point[6],
                          'keywname':data_point[7],
                          'keywvalue': float(data_point[8]),
                          'logtext':data_point[9],
                          'errstack': data_point[10],
                          'errstackidx': data_point[11],
                          'errlocation': data_point[12],
                          'errseverity': data_point[13],
                        },
            }

def csv_es_vltlog_generator_data(data,index, doc_type):
    for data_point in data:
        yield {
            '_index': index,
            '_type': doc_type,
            '_id': xxhash.xxh64(str(data_point[10])+str(data_point[11])+str(data_point[12])+str(data_point[13])).hexdigest()+xxhash.xxh64(str(data_point[1])+str(data_point[0])+str(data_point[2])+str(data_point[3])+str(data_point[4])+str(data_point[5])+str(data_point[6])+str(data_point[7])+str(data_point[8])+str(data_point[9])).hexdigest(),
            '_source':  {
                          '@timestamp': data_point[1],
                          'loghost': data_point[2] ,
                          'envname': data_point[3],
                          'procname':data_point[4],
                          'procid':data_point[5],
                          'module':data_point[6],
                          'keywname':data_point[7],
                          'keywvalue': data_point[8],
                          'logtext':data_point[9],
                          'errstack': data_point[10],
                          'errstackidx': data_point[11],
                          'errlocation': data_point[12],
                          'errseverity': data_point[13],
                        },
            }



CSV_ES_VLTLOG_OPSLOG_GENERATORS_DATA = {
    'vltlog': csv_es_vltlog_generator_data,
    'opslog': csv_es_opslog_generator_data
}

CSV_ES_BASIC_INDEXES = ['vltlog', 'opslog']
CSV_ES_BASIC_INDEXES_FILTERS = {
    'vltlog': lambda data_point: not csv_opslog_filter(data_point),
    'opslog': csv_opslog_filter,
}

CSV_ES_BASIC_DOC_TYPES = {
    'vltlog': ['fpar', 'err', 'flog', 'fevt', 'log'],
    'opslog': ['opslog']
}

CSV_ES_BASIC_DOC_TYPES_FILTERS = {
    'vltlog': {
        'fpar': lambda data_point: data_point[0].lower() == 'fpar',
        'err': lambda data_point: data_point[0].lower() == 'err',
        'flog': lambda data_point: data_point[0].lower() == 'flog',
        'fevt': lambda data_point: data_point[0].lower() == 'fevt',
        'log': lambda data_point: data_point[0].lower() == 'log',
    },
    'opslog': {
        'opslog': lambda data_point: data_point[0].lower() == 'fpar',
        # WE ALREADY INSERTED DATA WHEN I SEE THIS MISTAKE (doc_type should be fpar moraly)
    }
}


def csv_es_import(path_to_csv, es_server, chunksize=50000, header=CSV_VLTLOG_OPSLOG_HEADER,
                  indexes=CSV_ES_BASIC_INDEXES, indexes_filters=CSV_ES_BASIC_INDEXES_FILTERS, index_suffix=None,
                  doc_types=CSV_ES_BASIC_DOC_TYPES, doc_types_filters=CSV_ES_BASIC_DOC_TYPES_FILTERS,
                  es_generator_data=CSV_ES_VLTLOG_OPSLOG_GENERATORS_DATA):
    df = pd.read_csv(filepath_or_buffer=path_to_csv, names=header, compression='gzip', na_values=[""],
                     parse_dates=['tm'], engine='c', encoding='latin-1',
                     na_filter=False,
                     chunksize=chunksize)

    for chunk in df:
        try:
           result = es_insert_2(es_server, chunk.values, indexes, indexes_filters, index_suffix,
                                                     doc_types, doc_types_filters, es_generator_data)  # ,callback=callBack)
        except ConnectionTimeout as timeout: #THE GC is doing hard work
            datalab_logger_csvInserters.error(timeout)
            time.sleep(miscellaneous.CONNECTION_TIMEOUT_PAUSE)
    return result


def csv_import_file(path_to_csv, kairos_server, es_server, es_chunksize=50000,
                    header=CSV_VLTLOG_OPSLOG_HEADER,
                    kairos_filter=csv_opslog_filter, kairos_parser=csv_kairos_parser,
                    indexes=CSV_ES_BASIC_INDEXES, indexes_filters=CSV_ES_BASIC_INDEXES_FILTERS, index_suffix=None, doc_types=CSV_ES_BASIC_DOC_TYPES,
                    doc_types_filters=CSV_ES_BASIC_DOC_TYPES_FILTERS, es_generator_data=CSV_ES_VLTLOG_OPSLOG_GENERATORS_DATA):
    df = pd.read_csv(filepath_or_buffer=path_to_csv, names=header, compression='gzip', na_values=[""],
                     parse_dates=['tm'], engine='c', encoding='latin-1', na_filter=False, chunksize=es_chunksize)

    for chunk in df:
        kairos_result=kairos_insert(chunk.values, kairos_server, kairos_filter, kairos_parser)  # ,callback=callBack)
        try:
            es_result=es_insert_2(es_server, chunk.values, indexes, indexes_filters, index_suffix, doc_types, doc_types_filters, es_generator_data)
        except ConnectionTimeout as timeout: #THE GC is doing hard work
            datalab_logger_csvInserters.error(timeout)
            time.sleep(miscellaneous.CONNECTION_TIMEOUT_PAUSE)
    return (kairos_result, es_result)


def csv_datalab_import(path_to_csv, kairos_server, es_server, es_chunksize=50000,
                       header=CSV_VLTLOG_OPSLOG_HEADER,
                       kairos_filter=csv_opslog_filter, kairos_parser=csv_kairos_parser,
                       indexes=CSV_ES_BASIC_INDEXES, indexes_filters=CSV_ES_BASIC_INDEXES_FILTERS, index_suffix=None,
                       doc_types=CSV_ES_BASIC_DOC_TYPES, doc_types_filters=CSV_ES_BASIC_DOC_TYPES_FILTERS,
                       es_generator_data=CSV_ES_VLTLOG_OPSLOG_GENERATORS_DATA):
    files = glob.glob(path_to_csv)
    total = 0;
    total_inserted = 0;
    bash = 0
    for mi_file in files: total += os.path.getsize(mi_file)
    for f in files:
        s = time.time()
        result = csv_import_file(f, kairos_server, es_server, es_chunksize, header, kairos_filter,
                                 kairos_parser, indexes, indexes_filters, index_suffix,
                                 doc_types, doc_types_filters, es_generator_data)
        total_inserted += os.path.getsize(f);
        bash += os.path.getsize(f)
        if (bash / 1000000) > 20:  # Cada 100MB damos un respiro al sistema
            time.sleep(5)
            bash = 0
        # timeToFinish=int((((total/total_inserted)*(time.time()-s))+s)-time.time())/60
        datalab_logger_csvInserters.info("Inserted: %s file in %.2f secs, %.2f MB-%.2f MB" % (
            f, time.time() - s, total_inserted / 1000000.0, total / 1000000.0))
    return result
