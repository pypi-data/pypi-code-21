import urllib3
import simplejson
import sys
import argparse
from time import sleep
from time import mktime
from utils.rpc import RPC
from tools import resultview
from dateparser import parse

parser = argparse.ArgumentParser(description='Logtailer for Dashbase')
parser.add_argument("-n", "--num", type=int, default=10, help="number of lines to return")
parser.add_argument("-a", "--addr", type=str, required=True, help="Log address, e.g. table@host:port")
parser.add_argument("-q", "--query", type=str, default=None, help="query string")
parser.add_argument("-s", "--stream", type=bool, default=False, help="streaming mode")
parser.add_argument("-d", "--delay", type=int, default=5, help="delay in seconds in streaming mode")
parser.add_argument("-t", "--time", type=str, default="5 min ago",
                    help="time filter, e.g. May 20 2017 10:11:13,10 min ago")


def doQuery(rpc, req):
    response = rpc.do_post("/v1/query", req)
    data = response.data
    result = simplejson.loads(data)
    resultview.printResult(result)
    return result


def main():
    args = parser.parse_args()
    # dashbase request
    dashbase_req = {}

    if "@" not in args.addr:
        table = None
        url = args.addr
    else:
        table, url = args.addr.split("@", 1)

    rpc = RPC(url)

    if "," not in args.time:
        t1 = parse(args.time)
        if t1 == None:
            sys.exit("unable parse time: " + args.time)
        t2 = None
    else:
        s1, s2 = args.time.split(",", 1)
        t1 = parse(s1)
        if t1 == None:
            sys.exit("unable parse time: " + s1)
        t2 = parse(s2)
        if t2 == None:
            sys.exit("unable parse time: " + s2)

    time_filter = {}
    if t1 != None:
        # print "start time: " + str(t1)
        time_filter["startTimeInSec"] = mktime(t1.timetuple())
    if t2 != None:
        # print "end time: " + str(t2)
        time_filter["endTimeInSec"] = mktime(t2.timetuple())

    dashbase_req["timeRangeFilter"] = time_filter

    dashbase_req["disableHighlight"] = True
    dashbase_req["numResults"] = args.num

    dashbase_req["tableNames"] = []
    if table != None:
        dashbase_req["tableNames"].append(table)

    if args.query != None:
        query = {}
        query["queryType"] = "string"
        query["queryStr"] = args.query
        dashbase_req["query"] = query

    if args.stream:
        try:
            while True:
                try:
                    result = doQuery(rpc, dashbase_req)
                    if "startId" in result:
                        dashbase_req["endId"] = result["startId"]
                except urllib3.exceptions.HTTPError as e:
                    print "problem executing query, will try agin" + str(e)
                sleep(args.delay)
        except KeyboardInterrupt:
            print("Goodbye!")
    else:
        print dashbase_req
        result = doQuery(rpc, dashbase_req)
        print "found docs: {:,} / {:,}".format(result["numDocs"], result["totalDocs"])
    rpc.close()
