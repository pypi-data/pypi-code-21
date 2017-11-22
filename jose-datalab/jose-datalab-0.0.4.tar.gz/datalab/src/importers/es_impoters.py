import math
from enum import Enum
import datetime

import xxhash as xxhash
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk, parallel_bulk

from datalab.src.connections.connections import es_connection_setUp
from datalab.src.loggers import datalab_loggers

datalab_logger_es_object = datalab_loggers.datalab_logger(my_format=datalab_loggers.DATALAB_LOGGER_FORMAT)
datalab_logger_es_inserters = datalab_logger_es_object.datalab_logger

def es_create_index(es_server, index, mapping):
    es_object = es_connection_setUp(es_server)
    es_object.indices.create(index=index, body=mapping)

def es_vltlogs_generator_data(data, index, doc_type):
    for data_point in data:
        yield {
            '_index': index,
            '_type': doc_type,
            '_id': xxhash.xxh64(str(data_point[10]) + str(data_point[11]) + str(data_point[12]) + str(
                data_point[13])).hexdigest() + xxhash.xxh64(
                str(data_point[1]) + str(data_point[0]) + str(data_point[2]) + str(data_point[3]) + str(
                    data_point[4]) + str(data_point[5]) + str(data_point[6]) + str(data_point[7]) + str(
                    data_point[8]) + str(data_point[9])).hexdigest(),
            '_source': {
                '@timestamp': data_point[1],
                'loghost': data_point[2],
                'envname': data_point[3],
                'procname': data_point[4],
                'procid': data_point[5],
                'module': data_point[6],
                'keywname': data_point[8],
                'keywvalue': data_point[9],
                'logtext': data_point[10],
                'errstack': data_point[11],
                'errstackidx': data_point[12],
                'errlocation': data_point[13],
                'errseverity': data_point[14],
            },
        }


def es_opslogs_generator_data(data, index, doc_type):
    for data_point in data:
        yield {
            '_index': index,
            '_type': doc_type,
            '_id': xxhash.xxh64(str(data_point[10]) + str(data_point[11]) + str(data_point[12]) + str(
                data_point[13])).hexdigest() + xxhash.xxh64(
                str(data_point[1]) + str(data_point[0]) + str(data_point[2]) + str(data_point[3]) + str(
                    data_point[4]) + str(data_point[5]) + str(data_point[6]) + str(data_point[7]) + str(
                    data_point[8]) + str(data_point[9])).hexdigest(),
            '_source': {
                '@timestamp': data_point[1],
                'loghost': data_point[2],
                'envname': data_point[3],
                'procname': data_point[4],
                'procid': data_point[5],
                'module': data_point[6],
                'keywname': data_point[8],
                'keywvalue': float(data_point[9]),
                'logtext': data_point[10],
                'errstack': data_point[11],
                'errstackidx': data_point[12],
                'errlocation': data_point[13],
                'errseverity': data_point[14],
            },
        }


def opslog_filter(data_point):
    if data_point[7].lower() == 'fpar':
        try:
            x = float(data_point[9])
            if math.isnan(x) or math.isinf(x): return False
            return True
        except:
            return False
    else:
        return False


ES_VLTLOG_OPSLOG_GENERATORS_DATA = {
    'vltlog': es_vltlogs_generator_data,
    'opslog': es_opslogs_generator_data
}

ES_BASIC_INDEXES = ['vltlog', 'opslog']
ES_BASIC_INDEXES_FILTERS = {
    'vltlog': lambda data_point: not opslog_filter(data_point),
    'opslog': opslog_filter,
}

ES_BASIC_DOC_TYPES = {
    'vltlog': ['fpar', 'err', 'flog', 'fevt', 'log'],
    'opslog': ['opslog']
}

ES_BASIC_DOC_TYPES_FILTERS = {
    'vltlog': {
        'fpar': lambda data_point: data_point[7].lower() == 'fpar',
        'err': lambda data_point: data_point[7].lower() == 'err',
        'flog': lambda data_point: data_point[7].lower() == 'flog',
        'fevt': lambda data_point: data_point[7].lower() == 'fevt',
        'log': lambda data_point: data_point[7].lower() == 'log',
    },
    'opslog': {
        'opslog': lambda data_point: data_point[7].lower() == 'fpar',
        # WE ALREADY INSERTED DATA WHEN I SEE THIS MISTAKE (doc_type should be fpar moraly)
    }
}


def _get_index_with_suffix_name(es_index_name, suffix):
    """ Return elasticsearch index name
    :param: index_name the prefix to be used in the index
    :return: A srting containing the elasticsearch indexname used which should include the suffix
    """
    if suffix:
        return "{0!s}-{1!s}".format(es_index_name, suffix)
    else:
        return es_index_name


def es_insert(es_object, data, indexes=ES_BASIC_INDEXES, indexes_filters=ES_BASIC_INDEXES_FILTERS,
              index_suffix=None,
              doc_types=ES_BASIC_DOC_TYPES, doc_types_filters=ES_BASIC_DOC_TYPES_FILTERS,
              es_generator_data=ES_VLTLOG_OPSLOG_GENERATORS_DATA, bulk_fn=streaming_bulk):
    ok = True;
    result = "NO_INSERTED"
    datalab_logger_es_inserters.info("ES : Inserting data")
    for index in indexes:
        for doc_type in doc_types[index]:
            for ok, result in bulk_fn(es_object, es_generator_data[index](
                    list(filter(doc_types_filters[index][doc_type], list(filter(indexes_filters[index], data)))),
                    _get_index_with_suffix_name(index, index_suffix),
                    doc_type)): pass;
    datalab_logger_es_inserters.info(
        "ES : Finish Insert Chunk : Ok? %s" % ok)  # WE DON'T COLLECT RESULTS FOR PERFORMENCES REASONS

    return (ok, result)


def es_insert_2(es_server, data, indexes=ES_BASIC_INDEXES, indexes_filters=ES_BASIC_INDEXES_FILTERS,
                index_suffix=None,
                doc_types=ES_BASIC_DOC_TYPES, doc_types_filters=ES_BASIC_DOC_TYPES_FILTERS,
                es_generator_data=ES_VLTLOG_OPSLOG_GENERATORS_DATA, bulk_fn=streaming_bulk):
    ok = True;
    result = "NO_INSERTED"
    es_object = es_connection_setUp(es_server)
    datalab_logger_es_inserters.info("ES : Inserting data")

    for index in indexes:
        for doc_type in doc_types[index]:
            for ok, result in bulk_fn(es_object, es_generator_data[index](
                    list(filter(doc_types_filters[index][doc_type], list(filter(indexes_filters[index], data)))),
                    _get_index_with_suffix_name(index, index_suffix),
                    doc_type)): pass;
    datalab_logger_es_inserters.info(
        "ES : Finish Insert Chunk : Ok? %s" % ok)  # WE DON'T COLLECT RESULTS FOR PERFORMENCES REASONS
    return (ok, result)
