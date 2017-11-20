import unittest
import datetime, time

from datalab.miscellaneous import SuffixNameFrecuency
from datalab.src.connections.connections import DB_SESSION, es_connection_setUp, db_connection_setUp
from datalab.src.importers import collectors_importers
from datalab.src.importers.collectors_importers import collector_datalab_period, collector_datalab_present, \
    collector_datalab_backwards, collector_datalab_period_2

UPDATETIME=2


def _es_is_data(es_object, index, doc_type, timestamp1, timestamp2):

    result = es_object.search(
        index=index,
        doc_type=doc_type,
        body={
          'query': {
            'range': {
                "@timestamp":{
                    "gte": timestamp1,
                    "lte": timestamp2
                }
            }
          }
        }
    )
    return result['hits']['total']

class MyTestCase(unittest.TestCase):
    def test_collector_datalab_period(self):
        db_connection = db_connection_setUp(DB_SESSION)
        kairos_server = "http://134.171.189.10:8080"
        es_object = es_connection_setUp("134.171.189.10:9200")
        present = datetime.datetime.utcnow()
        past= present - datetime.timedelta(seconds=10)
        period = (past, present)
        collector_datalab_period(db_connection, period, kairos_server, es_object, index_suffix="test_collector_datalab_period")
        time.sleep(UPDATETIME)
        self.assertGreater(_es_is_data(es_object, 'vltlog', 'fpar', past, present), 0)

    def test_collector_datalab_present(self):
        collectors_importers.set_debug(True)
        db_connection = db_connection_setUp(DB_SESSION)
        kairos_server = "http://134.171.189.10:8080"
        es_object = es_connection_setUp("134.171.189.10:9200")
        delay=100
        past = datetime.datetime.utcnow() - datetime.timedelta(seconds=delay)
        present = past + datetime.timedelta(seconds=100)
        collector_datalab_present(db_connection, kairos_server, es_object, delay=delay, index_suffix_frecuency=SuffixNameFrecuency.MONTHLY)
        time.sleep(UPDATETIME)
        self.assertGreater(_es_is_data(es_object, 'vltlog', 'fpar', past, present), 0)

    def test_collector_datalab_backwards(self):
        collectors_importers.set_debug(True)
        db_connection = db_connection_setUp(DB_SESSION)
        kairos_server = "http://134.171.189.10:8080"
        es_object = es_connection_setUp("134.171.189.10:9200")
        start=datetime.datetime(2017,9,25,4,11,23)
        past=start-datetime.timedelta(seconds=10)
        collector_datalab_backwards(db_connection, kairos_server, es_object, start=start, index_suffix_frecuency=SuffixNameFrecuency.DAILY)
        time.sleep(UPDATETIME)
        self.assertGreater(_es_is_data(es_object, 'vltlog', 'fpar', past, start), 0)

    def test_datalab_period_2(self):
        db_connection = db_connection_setUp(DB_SESSION)
        kairos_server = "http://134.171.189.10:8080"
        es_object = es_connection_setUp("134.171.189.10:9200")
        start=datetime.datetime(2016,10,25,4,11,23)
        past=start-datetime.timedelta(seconds=100)
        period=(past,start)
        collector_datalab_period_2(db_connection, kairos_server, es_object, period, index_suffix_frecuency=SuffixNameFrecuency.DAILY)
        time.sleep(UPDATETIME)
        self.assertGreater(_es_is_data(es_object, 'vltlog', 'fpar', past, start), 0)

if __name__ == '__main__':
    unittest.main()
