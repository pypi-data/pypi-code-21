import datetime
import json
import requests
import gateway_helpers


URL = gateway_helpers.BASE_URL + '/utilization'
HEADERS = gateway_helpers.get_headers()
TESTRIG_ID = gateway_helpers.COMMON_SETTINGS["HARDWARENAME"]
DT_FORMAT = "%Y-%m-%d %H:%M:%S"


def record_start(testrig_id=TESTRIG_ID):
    # create the data for recording start
    dt_now = datetime.datetime.now()
    start_timestamp = datetime.datetime.strftime(dt_now, DT_FORMAT)
    data_for_start = {
        "testrig_id": testrig_id,
        "start": start_timestamp,
    }
    # post data to api to record start time
    try:
        requests.post(URL, data=json.dumps(data_for_start), headers=HEADERS)
    except Exception as e:
        print("Exception in record_start() " + e)


def record_end(testrig_id=TESTRIG_ID):
    # create the data for recording end
    dt_now = datetime.datetime.now()
    end_timestamp = datetime.datetime.strftime(dt_now, DT_FORMAT)
    data_for_end = {
        "testrig_id": testrig_id,
        "end": end_timestamp,
    }
    # post data to api to record end time
    try:
        requests.post(URL, data=json.dumps(data_for_end), headers=HEADERS)
    except Exception as e:
        print("Exception in record_start() " + e)
