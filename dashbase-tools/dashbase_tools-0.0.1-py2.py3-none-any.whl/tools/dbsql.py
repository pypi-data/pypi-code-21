#!/usr/bin/env python

import argparse
import simplejson
import urllib
import urllib3
from cmd import Cmd

from utils.rpc import RPC
from tools import resultview


class DashbaseConsole(Cmd):
    """Dashbase Commandline Console"""

    def __init__(self, rpc, jsonout):
        Cmd.__init__(self)
        self.rpc = rpc
        self.jsonout = jsonout

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
            result = simplejson.loads(data)
            if self.jsonout:
                resultview.printJson(result)
            else:
                resultview.print_schma(name, result)
        except urllib3.exceptions.HTTPError as e:
            self.rpc.close()
            self.rpc.init_connection()
            print("problem executing query, please try again: " + str(e))

    def do_table(self, name):
        """show table information"""

        if not name or len(name) == 0:
            url = "/v1/cluster/all"
        else:
            url = "/v1/cluster/" + name
        try:
            response = self.rpc.do_get(url)
            data = response.data
            result = simplejson.loads(data)
            if self.jsonout:
                resultview.printJson(result)
            else:
                if "overview" in result.keys():
                    overview = result["overview"]
                    resultview.print_cluster(name, overview)
                else:
                    print("unable to get table list")
        except urllib3.exceptions.HTTPError as e:
            self.rpc.close()
            self.rpc.init_connection()
            print("problem executing query, please try again: " + str(e))

    def do_debug(self, query):
        param = {"sql": "debug " + query}
        return self.execSelect(param)

    def do_select(self, query):
        param = {"sql": "select " + query}
        return self.execSelect(param)

    def execSelect(self, param):
        """runs a dashbase sql"""
        sql = urllib.urlencode(param)
        try:
            response = self.rpc.do_get("/v1/sql?" + sql)
            data = response.data
            result = simplejson.loads(data)
            if self.jsonout:
                resultview.printJson(result)
            else:
                if "error" in result:
                    print("Error: {}".format(result["error"]))
                else:
                    resultview.printAggregations(result["request"]["aggregations"], result["aggregations"])
                    resultview.printHits(result["request"]["fields"], result["hits"])
                    resultview.printTimeRange(result["request"])
                    resultview.printSearchStats(result)
                    resultview.printDebugInfo(result)
        except urllib3.exceptions.HTTPError as e:
            self.rpc.close()
            self.rpc.init_connection()
            print("problem executing query, please try again: " + str(e))

    def do_exit(self, s):
        """Exists the program."""
        print("Quitting.")
        raise SystemExit


def main():
    parser = argparse.ArgumentParser(description='Sql console for Dashbase')
    parser.add_argument("-a", "--address", type=str, required=True, help="Log name, e.g. host:port, required")
    parser.add_argument("-o", "--output", type=str, default=None, help="output format, e.g. json/None, default: None")
    args = parser.parse_args()
    rpc = RPC(args.address)
    jsonout = args.output is not None and args.output == "json"
    prompt = DashbaseConsole(rpc, jsonout)
    prompt.prompt = '> '
    prompt.cmdloop('Starting Dashbase console...')
    rpc.close()
