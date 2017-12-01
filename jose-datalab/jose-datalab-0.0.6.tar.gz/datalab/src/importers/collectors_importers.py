import datetime, time

from elasticsearch.helpers import parallel_bulk

from datalab.miscellaneous import SuffixNameFrecuency, _SUFFIX_FRECUENCY_FUNCION_DICT
from datalab.src.connections.connections import db_execute_query
from datalab.src.importers.datalab_importers import insert_datalab
from datalab.src.importers.es_impoters import ES_VLTLOG_OPSLOG_GENERATORS_DATA, ES_BASIC_DOC_TYPES_FILTERS, \
    ES_BASIC_DOC_TYPES, ES_BASIC_INDEXES_FILTERS, ES_BASIC_INDEXES
from datalab.src.importers.kairos_importers import kairos_insert, kairos_parser, kairos_filter, kairos_keep_alive
from datalab.src.loggers import datalab_loggers

datalab_logger_collector_object = datalab_loggers.datalab_logger(my_format=datalab_loggers.DATALAB_LOGGER_FORMAT)
datalab_logger_collecter_inserters = datalab_logger_collector_object.datalab_logger

DEBUG = False


def set_debug(boolean):
    global DEBUG
    DEBUG = boolean


def _getcollector_present_piglet(es_object, index, doc_type):
    body = {
        "query": {"match_all": {}},
        "size": 1,
        "sort": [{"collector_piglet": {"order": "desc"}}]
    }
    result = es_object.search(index=index, doc_type=doc_type, body=body)
    timestamp = result['hits']['hits'][0]['_source']['collector_piglet']
    x = datetime.datetime(year=int(timestamp[:4]), month=int(timestamp[5:7]), day=int(timestamp[8:10]),
                          hour=int(timestamp[11:13]), minute=int(timestamp[14:16]), \
                          second=int(timestamp[17:19]), microsecond=int(timestamp[20:]))  # 2017-10-17T23:06:23.165623
    return x


def _getcollector_backwards_piglet(es_object, index, doc_type):
    body = {
        "query": {"match_all": {}},
        "size": 1,
        "sort": [{"collector_piglet": {"order": "asc"}}]
    }
    result = es_object.search(index=index, doc_type=doc_type, body=body)
    timestamp = result['hits']['hits'][0]['_source']['collector_piglet']
    x = datetime.datetime(year=int(timestamp[:4]), month=int(timestamp[5:7]), day=int(timestamp[8:10]),
                          hour=int(timestamp[11:13]), minute=int(timestamp[14:16]), \
                          second=int(timestamp[17:19]), microsecond=int(timestamp[20:]))
    return x


def collector_datalab(db_connection, sql_sentence, sql_args, kairos_server, es_object, kairos_filter=kairos_filter,
                      kairos_parser=kairos_parser,
                      indexes=ES_BASIC_INDEXES, indexes_filters=ES_BASIC_INDEXES_FILTERS,
                      index_suffix=None, doc_types=ES_BASIC_DOC_TYPES,
                      doc_types_filters=ES_BASIC_DOC_TYPES_FILTERS, es_generator_data=ES_VLTLOG_OPSLOG_GENERATORS_DATA,
                      bulk_fn=parallel_bulk, fetchsize=1000):
    # es = es_connection_setUp([es_server])
    cursor = db_execute_query(db_connection, sql_sentence, sql_args)
    data = cursor.fetchmany(fetchsize)
    kairos_response = "NO_RESPONSE";
    n_data_inserted = 0;
    es_ok = True;
    es_result = 0;
    while data:
        (kairos_response, n_data_inserted, es_ok, es_result) = insert_datalab(data, kairos_server, es_object,
                                                                              kairos_filter,
                                                                              kairos_parser,
                                                                              indexes, indexes_filters,
                                                                              index_suffix, doc_types,
                                                                              doc_types_filters, es_generator_data,
                                                                              bulk_fn)
        data = cursor.fetchmany(fetchsize)
    return (kairos_response, n_data_inserted, es_ok, es_result)


def collector_datalab_period(db_connection, period, kairos_server, es_object, kairos_filter=kairos_filter,
                             kairos_parser=kairos_parser,
                             indexes=ES_BASIC_INDEXES, indexes_filters=ES_BASIC_INDEXES_FILTERS,
                             index_suffix=None,
                             doc_types=ES_BASIC_DOC_TYPES,
                             doc_types_filters=ES_BASIC_DOC_TYPES_FILTERS,
                             es_generator_data=ES_VLTLOG_OPSLOG_GENERATORS_DATA,
                             bulk_fn=parallel_bulk, fetchsize=1000):
    return collector_datalab(db_connection, "SELECT * FROM alog WHERE timestamp BETWEEN %s and %s", period,
                             kairos_server, es_object, kairos_filter, kairos_parser, indexes, indexes_filters,
                             index_suffix, doc_types,
                             doc_types_filters, es_generator_data, bulk_fn, fetchsize)


db_logger = datalab_loggers.datalab_logger(name="collector_presentLogger", index_es="collector_present_pigglet",
                                           my_format=datalab_loggers.DATALAB_LOGGER_FORMAT)
lastInserted_logger = db_logger.datalab_logger


def collector_datalab_present(db_connection, kairos_server, es_object, delay=100, kairos_filter=kairos_filter,
                              kairos_parser=kairos_parser,
                              indexes=ES_BASIC_INDEXES, indexes_filters=ES_BASIC_INDEXES_FILTERS,
                              index_suffix_frecuency=SuffixNameFrecuency.NONE, doc_types=ES_BASIC_DOC_TYPES,
                              doc_types_filters=ES_BASIC_DOC_TYPES_FILTERS,
                              es_generator_data=ES_VLTLOG_OPSLOG_GENERATORS_DATA,
                              bulk_fn=parallel_bulk, fetchsize=1000):
    delay = datetime.timedelta(seconds=delay)
    try:
        past = _getcollector_present_piglet(es_object,"collector_present_pigglet", "python_log")  # datetime.datetime.now();
        present = past + datetime.timedelta(seconds=100)
        while datetime.datetime.utcnow() - present > 0:  # Tenemos retraso! Hay que ponerse al dia e insertar sin delay
            index_suffix= _SUFFIX_FRECUENCY_FUNCION_DICT[index_suffix_frecuency](present)
            (response, n_data_inserted, es_ok, es_result) = collector_datalab_period(db_connection, (past, present),
                                                                                     kairos_server, es_object,
                                                                                     kairos_filter, kairos_parser,
                                                                                     indexes, indexes_filters, index_suffix,
                                                                                     doc_types, doc_types_filters,
                                                                                     es_generator_data, bulk_fn,
                                                                                     fetchsize)
            datalab_logger_collecter_inserters.info(
                "collector_datalab_present : Inserted period: time %s - %s" % (past, present))
            lastInserted_logger.info("collector_datalab_present: LAST_TIMESTAMP_INSERTED: %s %s" % (past, present),
                                     extra={'collector_piglet': present})

            past = present;
            present = past + datetime.timedelta(seconds=100)
        present = datetime.datetime.utcnow()
    except:  # No se ha encontrado al indice, esto quiere decir que nunca se ejecuto el collector
        past = datetime.datetime.utcnow() - datetime.timedelta(seconds=delay.total_seconds())
        present = past + datetime.timedelta(seconds=delay.total_seconds());

    time.sleep(delay.total_seconds())
    while True:
        index_suffix = _SUFFIX_FRECUENCY_FUNCION_DICT[index_suffix_frecuency](present)
        (response, n_data_inserted, es_ok, es_result) = collector_datalab_period(db_connection, (past, present),
                                                                                 kairos_server, es_object,
                                                                                 kairos_filter, kairos_parser,
                                                                                 indexes, indexes_filters, index_suffix,
                                                                                 doc_types, doc_types_filters,
                                                                                 es_generator_data, bulk_fn,
                                                                                 fetchsize)
        datalab_logger_collecter_inserters.info(
            "collector_datalab_present : Inserted period: time %s - %s" % (past, present))
        # datalab_logger_inserted.debug(response.text)
        lastInserted_logger.info("collector_datalab_present: LAST_TIMESTAMP_INSERTED: %s %s" % (past, present),
                                 extra={'collector_piglet': present})
        kairos_keep_alive(kairos_server, 'keepAlive.collector.present')
        past = present;
        datalab_logger_collecter_inserters.info(
            "collector_datalab_present : delay time %s" % str(
                datetime.datetime.utcnow() - past))
        present = datetime.datetime.utcnow()
        if present - past > delay:
            x = (present - past) - delay
            if x > delay:
                time.sleep(0)
            else:
                time.sleep(int((delay - x).total_seconds()))
        else:
            time.sleep(delay.total_seconds())
            # print(past, present)
            # print('2', int(((past + delay - present) + delay).total_seconds()))
            # time.sleep(int(((past + delay - present) + delay).total_seconds()))  # We try to control possible fluction inserting with delay time from alog.
        if DEBUG:  return (response, n_data_inserted, es_ok, es_result)


db2_logger = datalab_loggers.datalab_logger(name="collector_backwardsLogger", index_es="collector_backwards_piglet",
                                            my_format=datalab_loggers.DATALAB_LOGGER_FORMAT)
collector_backwardsLogger = db2_logger.datalab_logger


def collector_datalab_backwards(db_connection, kairos_server, es_object, start=-1, kairos_filter=kairos_filter,
                                kairos_parser=kairos_parser,
                                indexes=ES_BASIC_INDEXES, indexes_filters=ES_BASIC_INDEXES_FILTERS, index_suffix_frecuency=SuffixNameFrecuency.NONE,
                                doc_types=ES_BASIC_DOC_TYPES, doc_types_filters=ES_BASIC_DOC_TYPES_FILTERS,
                                es_generator_data=ES_VLTLOG_OPSLOG_GENERATORS_DATA,
                                bulk_fn=parallel_bulk, fetchsize=1000):
    if start != -1:
        past = start
    else:
        try:
            past = _getcollector_backwards_piglet(es_object,"collector_backwards_piglet", "python_log")  # datetime.datetime.now();
        except:
            past = datetime.datetime.utcnow();
    present = past - datetime.timedelta(seconds=100);
    while True:
        index_suffix = _SUFFIX_FRECUENCY_FUNCION_DICT[index_suffix_frecuency](present)
        result = collector_datalab_period(db_connection, (present, past), kairos_server, es_object, kairos_filter,
                                          kairos_parser, indexes, indexes_filters, index_suffix, doc_types, doc_types_filters,
                                          es_generator_data, bulk_fn, fetchsize)
        datalab_logger_collecter_inserters.info(
            "collector_datalab_backwards : Inserted period: time %s - %s" % (present, past))
        # datalab_logger_inserted.debug(result[0].text)
        collector_backwardsLogger.info("collector_datalab_backwards: LAST_TIMESTAMP_INSERTED: %s %s" % (present, past),
                                       extra={'collector_piglet': present})
        kairos_keep_alive(kairos_server, 'keepAlive.collector.backwards')
        past = present;
        present = present - datetime.timedelta(seconds=100)
        if DEBUG:  return result


def collector_datalab_period_2(db_connection, kairos_server, es_object, period, kairos_filter=kairos_filter,
                               kairos_parser=kairos_parser,
                               indexes=ES_BASIC_INDEXES, indexes_filters=ES_BASIC_INDEXES_FILTERS, index_suffix_frecuency=SuffixNameFrecuency.NONE,
                               doc_types=ES_BASIC_DOC_TYPES,
                               doc_types_filters=ES_BASIC_DOC_TYPES_FILTERS,
                               es_generator_data=ES_VLTLOG_OPSLOG_GENERATORS_DATA,
                               bulk_fn=parallel_bulk, fetchsize=1000):
    past = period[0]
    while True:
        if period[1] - past > datetime.timedelta(seconds=100):
            present = past + datetime.timedelta(seconds=100)
            datalab_logger_collecter_inserters.info(
                "collector_datalab_period : Inserted period: time %s - %s" % (past, present))
            index_suffix = _SUFFIX_FRECUENCY_FUNCION_DICT[index_suffix_frecuency](present)
            collector_datalab_period(db_connection, (past, present), es_object, kairos_server, kairos_filter,
                                     kairos_parser, indexes, indexes_filters, index_suffix, doc_types, doc_types_filters,
                                     es_generator_data, bulk_fn, fetchsize)
            past = present
        else:
            present = period[1]
            datalab_logger_collecter_inserters.info(
                "collector_datalab_period : Inserted period: time %s - %s" % (past, present))
            index_suffix = _SUFFIX_FRECUENCY_FUNCION_DICT[index_suffix_frecuency](present)
            collector_datalab_period(db_connection, (past, present), es_object, kairos_server, es_object, kairos_filter,
                                     kairos_parser, indexes, indexes_filters, index_suffix,doc_types, doc_types_filters,
                                     es_generator_data, bulk_fn, fetchsize)
            datalab_logger_collecter_inserters.info(
                "collector_datalab_period Finish: Terminado de insertar period: time %s - %s" % (period[0], period[1]))
            break;
