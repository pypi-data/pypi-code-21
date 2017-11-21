from __future__ import print_function

import argparse
import urllib
from cmd import Cmd

import urllib3

from tools import resultview
from utils.json import decode_json
from utils.rpc import RPC


class DashbaseConsole(Cmd):
    """Dashbase Commandline Console"""

    def __init__(self, rpc, json_out, **kwargs):
        Cmd.__init__(self, **kwargs)
        self.rpc = rpc
        self.json_out = json_out

    def handle_exception(self, e):
        self.rpc.close()
        self.rpc.init_connection()
        print("problem executing query, please try again: " + str(e))

    def do_schema(self, name):
        """shows table schemas"""
        if not name or len(name) == 0:
            url = "/v1/info"
        else:
            param = {"names": name}
            table_names = urllib.urlencode(param)
            url = "/v1/info?" + table_names
        try:
            response = self.rpc.do_get(url)
            data = response.data
            result = decode_json(data)
            if self.json_out:
                resultview.print_json(result)
            else:
                resultview.print_schema(name, result)
        except urllib3.exceptions.HTTPError as e:
            self.handle_exception(e)

    def do_table(self, name):
        """show table information"""

        if not name or len(name) == 0:
            url = "/v1/cluster/all"
        else:
            url = "/v1/cluster/" + name
        try:
            response = self.rpc.do_get(url)
            data = response.data
            result = decode_json(data)
            if self.json_out:
                resultview.print_json(result)
            else:
                if "overview" in result.keys():
                    overview = result["overview"]
                    resultview.print_cluster(name, overview)
                else:
                    print("unable to get table list")
        except urllib3.exceptions.HTTPError as e:
            self.handle_exception(e)

    def do_debug(self, query):
        param = {"sql": "debug " + query}
        return self.exec_select(param)

    def do_select(self, query):
        param = {"sql": "select " + query}
        return self.exec_select(param)

    def exec_select(self, param):
        """runs a dashbase sql"""
        sql = urllib.urlencode(param)
        try:
            response = self.rpc.do_get("/v1/sql?" + sql)
            data = response.data
            result = decode_json(data)
            if self.json_out:
                resultview.print_json(result)
            else:
                if "error" in result:
                    print("Error: {}".format(result["error"]))
                else:
                    resultview.print_aggregations(result["request"]["aggregations"], result["aggregations"])
                    resultview.print_hits(result["request"]["fields"], result["hits"])
                    resultview.print_time_range(result["request"])
                    resultview.print_search_stats(result)
                    resultview.print_debug_info(result)
        except urllib3.exceptions.HTTPError as e:
            self.handle_exception(e)

    def do_exit(self, s):
        """Exits the program."""
        print("Quitting.")
        return True


def main():
    parser = argparse.ArgumentParser(description='Sql console for Dashbase')
    parser.add_argument("-a", "--address", type=str, required=True, help="Log name, e.g. host:port, required")
    parser.add_argument("-o", "--output", type=str, default=None, help="output format, e.g. json/None, default: None")
    args = parser.parse_args()
    rpc = RPC(args.address)
    json_out = args.output is not None and args.output == "json"
    try:
        prompt = DashbaseConsole(rpc, json_out)
        prompt.prompt = '> '
        prompt.cmdloop('Starting Dashbase console... Press Ctrl+C or input "exit" to exit!')
    except KeyboardInterrupt:
        print('Goodbye!')
    rpc.close()
