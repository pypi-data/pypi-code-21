import unittest
import datetime, time

from datalab.src.connections.connections import es_connection_setUp
from datalab.src.importers.es_impoters import es_insert, es_insert_2

UPDATETIME=2

def _es_is_data(es_object, index, doc_type, id):

    result = es_object.search(
        index=index,
        doc_type=doc_type,
        body={
          'query': {
            'terms': {
              '_id': [id],
            }
          }
        }
    )
    return result['hits']['total']==1



class MyTestCase(unittest.TestCase):
    def test_es_insert(self):
        data = [(1546655907,datetime.datetime(2017,9,25,4,11,23),'wat3tcs','lat3vcm','logManager',0,'','FPAR','TESTER_ES_INSERT','4.6692','Es Trascendente','',0,'',''),\
                (1546636293,datetime.datetime(2017,9,25,4,12,27),'wat4tcs','lat4vcm','logManager',0,'','FPAR','TESTER_ES_INSERT','1.6180','La perfeccion.','',0,'',''),
                (1546616293, datetime.datetime(2017, 9, 25, 4, 12, 27), 'wat4tcs', 'lat4vcm', 'logManager', 0, '', 'FPAR', 'TESTER_ES_INSERT', 'ESTONOESUNNUMERO', 'La perfeccion.', '', 0, '', ''),
                (1546616293, datetime.datetime(2017, 9, 25, 4, 12, 27), 'wat4tcs', 'lat4vcm', 'logManager', 0, '','LOG', 'TESTER_ES_INSERT', 'ESTONOESUNNUMERO', 'La perfeccion.', '', 0, '', '')]
        es = es_connection_setUp("134.171.189.10:9200")
        (ok, result) = es_insert(es_object=es, data=data, index_suffix="test_es_insert".lower())
        time.sleep(UPDATETIME)
        self.assertEqual(ok, True)
        self.assertTrue(_es_is_data(es, index="opslog-test_es_insert", doc_type="opslog", id="afa98a536c513056ac60368c222bda4c"))
        self.assertTrue(_es_is_data(es, index="opslog", doc_type="opslog", id="9bde7bc7e466ab8db180492c96020d5b"))
        self.assertTrue(_es_is_data(es, index="vltlog-test_es_insert", doc_type="fpar", id="afa98a536c513056689fa883f14f831a"))
        self.assertTrue(_es_is_data(es, index="vltlog", doc_type="log", id="afa98a536c513056ae1269ccf4fd8807"))
        es.delete(index="opslog-test_es_insert", doc_type="opslog", id="afa98a536c513056ac60368c222bda4c")
        es.delete(index="opslog-test_es_insert", doc_type="opslog", id="9bde7bc7e466ab8db180492c96020d5b")
        es.delete(index="vltlog-test_es_insert", doc_type="fpar", id="afa98a536c513056689fa883f14f831a")
        es.delete(index="vltlog-test_es_insert", doc_type="log", id="afa98a536c513056ae1269ccf4fd8807")

    def test_es_insert_2(self):
        data = [(1546655907,datetime.datetime(2017,9,25,4,11,23),'wat3tcs','lat3vcm','logManager',0,'','FPAR','TESTER_ES_INSERT','4.6692','Es Trascendente','',0,'',''),\
                (1546636293,datetime.datetime(2017,9,25,4,12,27),'wat4tcs','lat4vcm','logManager',0,'','FPAR','TESTER_ES_INSERT','1.6180','La perfeccion.','',0,'',''),
                (1546616293, datetime.datetime(2017, 9, 25, 4, 12, 27), 'wat4tcs', 'lat4vcm', 'logManager', 0, '', 'FPAR', 'TESTER_ES_INSERT', 'ESTONOESUNNUMERO', 'La perfeccion.', '', 0, '', ''),
                (1546616293, datetime.datetime(2017, 9, 25, 4, 12, 27), 'wat4tcs', 'lat4vcm', 'logManager', 0, '','LOG', 'TESTER_ES_INSERT', 'ESTONOESUNNUMERO', 'La perfeccion.', '', 0, '', '')]
        (ok, result) = es_insert_2(es_server="134.171.189.10:9200", data=data, index_suffix="test_es_insert_2".lower())
        time.sleep(UPDATETIME)
        self.assertEqual(ok, True)
        es = es_connection_setUp("134.171.189.10:9200")
        self.assertTrue(_es_is_data(es, index="opslog-test_es_insert_2", doc_type="opslog", id="afa98a536c513056ac60368c222bda4c"))
        self.assertTrue(_es_is_data(es, index="opslog", doc_type="opslog", id="9bde7bc7e466ab8db180492c96020d5b"))
        self.assertTrue(_es_is_data(es, index="vltlog-test_es_insert_2", doc_type="fpar", id="afa98a536c513056689fa883f14f831a"))
        self.assertTrue(_es_is_data(es, index="vltlog", doc_type="log", id="afa98a536c513056ae1269ccf4fd8807"))
        es.delete(index="opslog-test_es_insert_2", doc_type="opslog", id="afa98a536c513056ac60368c222bda4c")
        es.delete(index="opslog-test_es_insert_2", doc_type="opslog", id="9bde7bc7e466ab8db180492c96020d5b")
        es.delete(index="vltlog-test_es_insert_2", doc_type="fpar", id="afa98a536c513056689fa883f14f831a")
        es.delete(index="vltlog-test_es_insert_2", doc_type="log", id="afa98a536c513056ae1269ccf4fd8807")



if __name__ == '__main__':
    unittest.main()
