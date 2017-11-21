import urllib

import simplejson
import urllib3

from utils.json import decode_json


class DashbaseClient(object):
    def __init__(self, rpc):
        self.rpc = rpc

    def handle_exception(self, e):
        self.rpc.close()
        self.rpc.init_connection()
        print("problem executing query, please try again: " + str(e))

    def get_tables(self):
        url = "/v1/cluster/all"
        try:
            response = self.rpc.do_get(url)
            data = response.data
            if "overview" in data:
                result = decode_json(data)
                return result["overview"].keys()
        except urllib3.exceptions.HTTPError as e:
            self.handle_exception(e)

    def get_info(self, table_name):
        url = "/v1/cluster/{}".format(table_name)
        try:
            response = self.rpc.do_get(url)
            return response.data
        except urllib3.exceptions.HTTPError as e:
            self.handle_exception(e)

    def get_schema(self, table_name):
        url = "/v1/info?names={}".format(table_name)
        try:
            response = self.rpc.do_get(url)
            return response.data
        except urllib3.exceptions.HTTPError as e:
            self.handle_exception(e)

    def get_data(self, sql):
        if not sql:
            sql = 'select *'
        sql = urllib.urlencode({'sql': sql})
        r = self.rpc.do_get("/v1/sql?" + sql)
        return simplejson.dumps(decode_json(r.data)['hits'], indent=4, sort_keys=True)
