from datalab.src.importers.es_impoters import es_insert, ES_BASIC_INDEXES, ES_BASIC_INDEXES_FILTERS, ES_BASIC_DOC_TYPES, \
    ES_BASIC_DOC_TYPES_FILTERS, ES_VLTLOG_OPSLOG_GENERATORS_DATA
from datalab.src.importers.kairos_importers import kairos_insert, kairos_parser, kairos_filter
from elasticsearch.helpers import streaming_bulk, parallel_bulk


def insert_datalab(data, kairos_server, es_object, kairos_filter=kairos_filter, kairos_parser=kairos_parser,
                   indexes=ES_BASIC_INDEXES, indexes_filters=ES_BASIC_INDEXES_FILTERS,
                   index_suffix=None, doc_types=ES_BASIC_DOC_TYPES,
                   doc_types_filters=ES_BASIC_DOC_TYPES_FILTERS, es_generator_data=ES_VLTLOG_OPSLOG_GENERATORS_DATA,
                   bulk_fn=parallel_bulk):
    n_data_inserted = 0;
    response = None
    (kairos_response, n_data_inserted) = kairos_insert(data, kairos_server, kairos_filter, kairos_parser)
    (es_ok, es_result) = es_insert(es_object, data, indexes, indexes_filters, index_suffix, doc_types,
                                   doc_types_filters,
                                   es_generator_data, bulk_fn)
    return (kairos_response, n_data_inserted, es_ok, es_result)
