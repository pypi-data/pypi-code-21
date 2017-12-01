import unittest
import datetime, time

import requests, json

from datalab.src.connections.connections import es_connection_setUp
from datalab.src.importers.datalab_importers import insert_datalab
from datalab.src.importers.kairos_importers import kairos_filter

UPDATETIME=2

def _get_number_data_points(server, metric):
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
        "start_relative": {
        "value": "15",
        "unit": "years"
        }
    }
    response = requests.post(server + "/api/v1/datapoints/query", data=json.dumps(query))
    return int(response.json()['queries'][0]['sample_size'])

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
    def  test_insert_datalab(self):
        data = [(1546655907, datetime.datetime(2016, 8, 25, 4, 10, 23), 'wat3tcs', 'lat3vcm', 'logManager', 0, '',
                 'FPAR', 'TESTER_DATALAB_INSERT', '4.669201', 'Es Trascendente', '', 0, '', ''),
                (1546636293, datetime.datetime(2016, 8, 25, 4, 12, 27), 'wat4tcs', 'lat4vcm', 'logManager', 0, '',
                 'LOG', 'TESTER_DATALAB_INSERT', 'ESTONOESUNNUMERO', 'La perfeccion.', '', 0, '', '')]
        kairos_server = "http://134.171.189.10:8080"
        es_object = es_connection_setUp("134.171.189.10:9200")
        (kairos_response, n_data_inserted, es_ok, es_result) = insert_datalab(data, kairos_server, es_object, index_suffix="pruebas")
        time.sleep(UPDATETIME)
        self.assertEqual(kairos_response.status_code, 204)
        self.assertEqual(_get_number_data_points("http://134.171.189.10:8080", 'TESTER_DATALAB_INSERT'),
                         len(list(filter(kairos_filter, data))))
        self.assertTrue(_es_is_data(es_object, index="opslog-pruebas", doc_type="opslog", id="9bde7bc7e466ab8dd1fa7f0e9b9482ec"))
        self.assertTrue(_es_is_data(es_object, index="vltlog-pruebas", doc_type="log", id="afa98a536c513056f6e7349c58d22390"))
        es_object.delete(index="opslog-pruebas", doc_type="opslog", id="9bde7bc7e466ab8dd1fa7f0e9b9482ec")
        es_object.delete(index="vltlog-pruebas", doc_type="log", id="afa98a536c513056f6e7349c58d22390")


if __name__ == '__main__':
    unittest.main()
