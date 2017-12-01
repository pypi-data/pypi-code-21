import unittest
import datetime
import requests
import json

from datalab.src.importers.kairos_importers import kairos_filter, kairos_parser, kairos_insert

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

class MyTestCase(unittest.TestCase):
    def test_kairos_insert(self):
        kairosdb_server="http://134.171.189.10:8080"
        data_filter=kairos_filter
        data_parser= kairos_parser
        data=[(1546655907,datetime.datetime(2017,9,25,4,11,23),'wat3tcs','lat3vcm','logManager',0,'','FPAR','TESTER_KAIROS_INSERT','2.7182818','Prueba msg','',0,'',''),\
              (1546636293,datetime.datetime(2017,9,25,4,12,27),'wat4tcs','lat4vcm','logManager',0,'','FPAR','TESTER_KAIROS_INSERT','3.1415926','Prueba msg','',0,'','')]
        (response, n_data_inserted) = kairos_insert(data, kairosdb_server, data_filter, data_parser)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(_get_number_data_points("http://134.171.189.10:8080", "TESTER_KAIROS_INSERT"), len(list(filter(data_filter, data))))


if __name__ == '__main__':
    unittest.main()

