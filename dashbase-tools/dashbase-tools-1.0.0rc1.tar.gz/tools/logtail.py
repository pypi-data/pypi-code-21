import argparse
import sys
from time import mktime, sleep

import urllib3
from dateparser import parse

from tools import resultview
from utils.json import decode_json
from utils.rpc import RPC

parser = argparse.ArgumentParser(description='Logtailer for Dashbase')
parser.add_argument("-n", "--num", type=int, default=10, help="number of lines to return")
parser.add_argument("-a", "--addr", type=str, required=True, help="Log address, e.g. table@host:port")
parser.add_argument("-q", "--query", type=str, default=None, help="query string")
parser.add_argument("-s", "--stream", type=bool, default=False, help="streaming mode")
parser.add_argument("-d", "--delay", type=int, default=5, help="delay in seconds in streaming mode")
parser.add_argument("-f", "--fields", type=str, default=None, help="fields to display")
parser.add_argument("-r", "--hideraw", type=bool, default=False, help="hide raw data")
parser.add_argument("-t", "--time", type=str, default="5 min ago",
                    help="time filter, e.g. May 20 2017 10:11:13,10 min ago")


def do_query(rpc, req, hide_raw):
    response = rpc.do_post("/v1/query", req)
    data = response.data
    result = decode_json(data)
    resultview.print_result(result, req["fields"], not hide_raw)
    return result


def main():
    args = parser.parse_args()
    # dashbase request
    dashbase_req = {}

    # parse addr
    if "@" not in args.addr:
        table = None
        url = args.addr
    else:
        table, url = args.addr.split("@", 1)

    # parse fields
    if args.fields:
        dashbase_req["fields"] = args.fields.split(",")
    else:
        dashbase_req["fields"] = None

    # init rpc
    rpc = RPC(url)

    # parse time
    if "," not in args.time:
        t1 = parse(args.time)
        if t1 is None:
            sys.exit("unable parse time: " + args.time)
        t2 = None
    else:
        s1, s2 = args.time.split(",", 1)
        t1 = parse(s1)
        if t1 is None:
            sys.exit("unable parse time: " + s1)
        t2 = parse(s2)
        if t2 is None:
            sys.exit("unable parse time: " + s2)

    # set time filter
    time_filter = {}
    if t1 is not None:
        time_filter["startTimeInSec"] = mktime(t1.timetuple())
    if t2 is not None:
        time_filter["endTimeInSec"] = mktime(t2.timetuple())

    # init dashbase request para
    dashbase_req["timeRangeFilter"] = time_filter
    dashbase_req["disableHighlight"] = True
    dashbase_req["numResults"] = args.num
    dashbase_req["tableNames"] = []
    if table is not None:
        dashbase_req["tableNames"].append(table)

    # parse query
    if args.query is not None:
        query = {"queryType": "string", "queryStr": args.query}
        dashbase_req["query"] = query

    if args.stream:
        try:
            while True:
                try:
                    result = do_query(rpc, dashbase_req, args.hideraw)
                    if "startId" in result:
                        dashbase_req["endId"] = result["startId"]
                except urllib3.exceptions.HTTPError as e:
                    print("problem executing query, will try again" + str(e))
                sleep(args.delay)
        except KeyboardInterrupt:
            print("Goodbye!")
    else:
        print(dashbase_req)
        result = do_query(rpc, dashbase_req, args.hideraw)
        print("found docs: {:,} / {:,}".format(result["numDocs"], result["totalDocs"]))
    rpc.close()
