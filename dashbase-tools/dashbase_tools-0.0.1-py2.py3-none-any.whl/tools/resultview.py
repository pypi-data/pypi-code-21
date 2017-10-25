import datetime
import json
from terminaltables import AsciiTable
from textwrap import wrap


def printJson(result):
    print(json.dumps(result, indent=4, sort_keys=True))


def hms_string(sec_elapsed):
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60.
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)


# End hms_string

def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def format_time_value(timeInSeconds):
    value = datetime.datetime.fromtimestamp(timeInSeconds)
    return value.strftime('%Y-%m-%d %H:%M:%S')


def rawPayload(hit):
    raw = "Not Available"
    if hit["payload"] != None:
        if "stored" in hit["payload"].keys():
            raw = raw = hit["payload"]["stored"]
    return raw


def printResult(result):
    hits = result["hits"]
    if (hits != None) and (len(hits) != 0):
        for hit in hits:
            raw = rawPayload(hit)
            timestamp = format_time_value(hit["timeInSeconds"])
            print("{}\t{}".format(timestamp, raw))


def drawNumericAggregation(name, numeric, aggr_req):
    headernames = ["numRows", "value"]
    data = []
    data.append(headernames)
    if name in aggr_req:
        aggr_req = aggr_req[name]
    title = "{}={}({})".format(name, aggr_req["type"], aggr_req["col"])
    table = AsciiTable(data, title)
    if numeric != None:
        numDocs = "{:,}".format(numeric["numDocs"])
        value = "{0:.2f}".format(numeric["value"])
        data.append([numDocs, value])
    return table.table


def printNumericAggregation(name, numeric, aggr_req):
    print(drawNumericAggregation(name, numeric, aggr_req))


def printTsAggregation(name, histograms):
    headernames = ["start", "end", "count"]
    data = []
    data.append(headernames)
    if histograms != None:
        interval = histograms["bucketSizeInSeconds"]
        title = name + "(interval = {})".format(hms_string(interval))
        table = AsciiTable(data, title)
        buckets = histograms["histogramBuckets"]
        for bucket in buckets:
            start = format_time_value(bucket["timeInSec"])
            end = format_time_value(bucket["timeInSec"] + interval)
            count = "{:,}".format(bucket["count"])
            data_array = [start, end, count]
            data.append(data_array)
    else:
        table = AsciiTable(data, name)
    print(table.table)


def drawTopnAggregation(name, topn):
    headernames = ["value", "count"]
    data = []
    data.append(headernames)
    if topn != None:
        col = topn["col"]
        title = name + "(column={})".format(col)
        table = AsciiTable(data, title)
        facets = topn["facets"]
        for facet in facets:
            count = "{:,}".format(facet["count"])
            data.append([facet["value"], count])
    else:
        table = AsciiTable(data, name)
    return table.table


def printTopnAggregation(name, topn):
    print drawTopnAggregation(name, topn)


def drawAggResp(agg, sub_req):
    aggStr = None
    if agg != None:
        aggType = agg["responseType"]
        if aggType == "numeric":
            aggStr = drawNumericAggregation(aggType, agg, sub_req)
        elif aggType == "topn":
            aggStr = drawTopnAggregation(aggType, agg)
    return aggStr


def printTsaAggregation(name, tsa, sub_req):
    headernames = ["start", "end", "bucket"]
    data = []
    data.append(headernames)
    if tsa != None:
        interval = tsa["bucketSizeInSeconds"]
        title = name + "(interval = {})".format(hms_string(interval))
        table = AsciiTable(data, title)
        buckets = tsa["buckets"]
        for bucket in buckets:
            start = format_time_value(bucket["timeInSec"])
            end = format_time_value(bucket["timeInSec"] + interval)
            aggStr = drawAggResp(bucket["response"], sub_req)
            if aggStr == None:
                aggStr = "n/a"
            data_array = [start, end, aggStr]
            data.append(data_array)
    else:
        table = AsciiTable(data, name)
    print(table.table)


def printAggregations(aggr_req, aggregations):
    if aggr_req != None and len(aggr_req) > 0:
        names = aggr_req.keys()
        for name in names:
            if name in aggregations.keys():
                agg = aggregations[name]
                if agg != None:
                    aggType = agg["responseType"]
                    if aggType == "ts":
                        printTsAggregation(name, agg)
                    elif aggType == "numeric":
                        printNumericAggregation(name, agg, aggr_req)
                    elif aggType == "topn":
                        printTopnAggregation(name, agg)
                    elif aggType == "tsa":
                        subReq = aggr_req[name]["subRequest"]
                        printTsaAggregation(name, agg, subReq)


def printTimeRange(request):
    t1 = None
    t2 = None
    if "timeRangeFilter" in request and request["timeRangeFilter"] is not None:
        t1 = datetime.datetime.fromtimestamp(
            request["timeRangeFilter"]["startTimeInSec"]
        ).strftime('%Y-%m-%d %H:%M:%S')
        t2 = datetime.datetime.fromtimestamp(
            request["timeRangeFilter"]["endTimeInSec"]
        ).strftime('%Y-%m-%d %H:%M:%S')
    print("Time range: from {} to {}".format(t1, t2))


def printDebugInfo(request):
    if "debugMap" in request and request["debugMap"] is not None:
        headernames = ["name", "value"]
        data = []
        data.append(headernames)
        for field in request["debugMap"]:
            dataArray = []
            dataArray.append(field)
            dataArray.append(request["debugMap"][field])
            data.append(dataArray)
        table = AsciiTable(data, "debug info")
        print (table.table)


def printSearchStats(result):
    latency = result["latencyInMillis"] / 1000.0
    time_string = "({0:.2f} sec)".format(latency)
    print("{:,} rows of {:,} {}, approximation = {}".format(result["numDocs"], result["totalDocs"], time_string,
                                                            result["request"]["useApproximation"]))


def printHits(fieldnames, hits):
    headernames = ["time"]
    if fieldnames != None:
        for field in fieldnames:
            if field != '_stored':
                headernames.append(str(field))
    headernames += ["RAW"]
    data = []
    data.append(headernames)
    table = AsciiTable(data, "Hits")
    for hit in hits:
        # first add time
        data_array = [format_time_value(hit["timeInSeconds"])]
        hitFields = hit["payload"]["fields"]

        data.append(data_array)
        if fieldnames != None:
            for field in fieldnames:
                if field != '_stored':
                    val = None
                    if field in hitFields.keys():
                        val = hitFields[field]
                    if val != None and len(val) > 0:
                        data_array.append(val[0])
                    else:
                        data_array.append("n/a")
        data_array.append("n/a")

    n = 1
    for hit in hits:
        raw_val = rawPayload(hit)
        if raw_val != None:
            max_width = table.column_max_width(len(headernames) - 1)
            wrapped_string = '\n'.join(wrap(raw_val, max_width))
            data[n][len(headernames) - 1] = wrapped_string
        n = n + 1
    print(table.table)


def print_schma(name, resp):
    try:
        headernames = ["column", "type"]
        data = []
        data.append(headernames)
        title = "{}:{} rows".format(name, resp["numDocs"])
        table = AsciiTable(data, title)

        schema = resp["schema"]
        if schema != None:
            for field in schema["fields"]:
                field_name = field["name"]
                if field["isKey"]:
                    colType = "key"
                elif field["isMeta"]:
                    colType = "meta"
                elif field["isNumeric"]:
                    colType = "numeric"
                else:
                    colType = "text"

                data.append([field_name, colType])
            print(table.table)
        else:
            print("table: {} not found".format(name))
    except:
        print("problem fetching schema for table: \"{}\"".format(name))


def print_cluster(name, overview_info):
    if name == None or len(name) == 0:
        print("tables: [{}]".format(",".join(overview_info.keys())))
        for table_name in overview_info.keys():
            print_table_info(table_name, overview_info[table_name])
    else:
        if "name" in overview_info:
            print_table_info(name, overview_info[name])
        else:
            print("table: \"" + name + "\" not found.")


def print_table_info(name, table_info):
    metrics_info = table_info["metrics"]

    metrics_data = [["type", "time unit", "volume"]]
    indexing_info = metrics_info["indexing"]
    metrics_data.append(["bytes", "per second", sizeof_fmt(indexing_info["numBytesPerSecond"])])
    metrics_data.append(["bytes", "per day", sizeof_fmt(indexing_info["numBytesPerDay"])])
    metrics_data.append(["events", "per second", "{:,}".format(indexing_info["numEventsPerSecond"])])
    metrics_data.append(["events", "per day", "{:,}".format(indexing_info["numEventsPerDay"])])

    metrics_table = AsciiTable(metrics_data, name + ": ingestion")
    print(metrics_table.table)

    cluster_info = table_info["info"]
    partitions_data = [["partition", "hosts"]]
    partitions_table = AsciiTable(partitions_data, name + ": partitions")
    for partition in cluster_info.keys():
        host_list = cluster_info[partition]
        partitions_data.append([partition, "\r".join(host_list)])
    print(partitions_table.table)
