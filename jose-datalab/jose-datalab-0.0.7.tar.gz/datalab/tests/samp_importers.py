import unittest
import requests, json

from datalab.src.importers.samp_importers import samp_import


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
    def test_samp_import(self):
        #path_to_samp="/Users/user/PycharmProjects/datalab/datalab/tests/vtosfSamplingAxis.2017-07-29T220529.ALT.samp"
        path_to_samp="/Users/user/PycharmProjects/datalab/datalab/tests/vtosfSamplingAxis.2017-07-29T220529.ALT.samp"
        kairos_server="http://134.171.189.10:8080"
        samp_import(path_to_samp, kairos_server)
        print(_get_number_data_points(kairos_server, "trackingAxis.vta.alt.POSLOOP.pos"))
        #self.assertEqual(_get_number_data_points(kairos_server, "trackingAxis.vta.az.POSLOOP.pos"),25612)

if __name__ == '__main__':
    unittest.main()
