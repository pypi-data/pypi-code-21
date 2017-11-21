from __future__ import print_function

import datetime
import json
from textwrap import wrap

from terminaltables import AsciiTable

from utils.highlight import highlight_str


def print_json(result):
    print(json.dumps(result, indent=4, sort_keys=True))


def hms_string(sec_elapsed):
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60.
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def format_time_value(time_in_seconds):
    value = datetime.datetime.fromtimestamp(time_in_seconds)
    return value.strftime('%Y-%m-%d %H:%M:%S')


def raw_payload(hit):
    raw = "Not Available"
    if hit["payload"] is not None:
        if "stored" in hit["payload"].keys():
            raw = hit["payload"]["stored"]
    return raw.encode('utf-8').strip()


def print_result(result, fields, show_raw):
    hits = result["hits"]
    print_hits(fields, hits, True, show_raw)


def draw_numeric_aggregation(name, numeric, aggr_req):
    header_names = ["numRows", "value"]
    data = [header_names]
    if name in aggr_req:
        aggr_req = aggr_req[name]
    title = "{}={}({})".format(name, aggr_req["type"], aggr_req["col"])
    table = AsciiTable(data, title)
    if numeric is not None:
        num_docs = "{:,}".format(numeric["numDocs"])
        value = "{0:.2f}".format(numeric["value"])
        data.append([num_docs, value])
    return table.table


def print_numeric_aggregation(name, numeric, aggr_req):
    print(draw_numeric_aggregation(name, numeric, aggr_req))


def print_ts_aggregation(name, histograms):
    header_names = ["start", "end", "count"]
    data = [header_names]
    if histograms is not None:
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


def draw_topn_aggregation(name, topn):
    header_names = ["value", "count"]
    data = [header_names]
    if topn is not None:
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


def print_topn_aggregation(name, topn):
    print(draw_topn_aggregation(name, topn))


def draw_agg_resp(agg, sub_req):
    agg_str = None
    if agg is not None:
        agg_type = agg["responseType"]
        if agg_type == "numeric":
            agg_str = draw_numeric_aggregation(agg_type, agg, sub_req)
        elif agg_type == "topn":
            agg_str = draw_topn_aggregation(agg_type, agg)
    return agg_str


def print_tsa_aggregation(name, tsa, sub_req):
    header_names = ["start", "end", "bucket"]
    data = [header_names]
    if tsa is not None:
        interval = tsa["bucketSizeInSeconds"]
        title = name + "(interval = {})".format(hms_string(interval))
        table = AsciiTable(data, title)
        buckets = tsa["buckets"]
        for bucket in buckets:
            start = format_time_value(bucket["timeInSec"])
            end = format_time_value(bucket["timeInSec"] + interval)
            agg_str = draw_agg_resp(bucket["response"], sub_req)
            if agg_str is None:
                agg_str = "n/a"
            data_array = [start, end, agg_str]
            data.append(data_array)
    else:
        table = AsciiTable(data, name)
    print(table.table)


def print_aggregations(aggr_req, aggregations):
    if aggr_req is not None and len(aggr_req) > 0:
        names = aggr_req.keys()
        for name in names:
            if name in aggregations.keys():
                agg = aggregations[name]
                if agg is not None:
                    agg_type = agg["responseType"]
                    if agg_type == "ts":
                        print_ts_aggregation(name, agg)
                    elif agg_type == "numeric":
                        print_numeric_aggregation(name, agg, aggr_req)
                    elif agg_type == "topn":
                        print_topn_aggregation(name, agg)
                    elif agg_type == "tsa":
                        sub_req = aggr_req[name]["subRequest"]
                        print_tsa_aggregation(name, agg, sub_req)


def print_time_range(request):
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


def print_debug_info(request):
    if "debugMap" in request and request["debugMap"] is not None:
        header_names = ["name", "value"]
        data = [header_names]
        for field in request["debugMap"]:
            data_array = [field, request["debugMap"][field]]
            data.append(data_array)
        table = AsciiTable(data, "debug info")
        print(table.table)


def print_search_stats(result):
    latency = result["latencyInMillis"] / 1000.0
    time_string = "({0:.2f} sec)".format(latency)
    print("{:,} rows of {:,} {}, approximation = {}".format(result["numDocs"], result["totalDocs"], time_string,
                                                            result["request"]["useApproximation"]))


def get_highlight_entity(hit):
    if 'payload' not in hit or 'entities' not in hit['payload']:
        return None
    entities = hit["payload"]["entities"]
    for entity in entities:
        if 'highlight' in entity:
            return entity["highlight"]
    return None


def get_hl_field_entities(hit, field):
    highlight_entity = get_highlight_entity(hit)
    if highlight_entity:
        if field not in highlight_entity['fields']:
            return None
        return highlight_entity["fields"][field]
    return None


def get_hl_stored_entities(hit):
    highlight_entity = get_highlight_entity(hit)
    if highlight_entity:
        if 'stored' not in highlight_entity:
            return None
        return highlight_entity["stored"]
    return None


def print_hits(fieldnames, hits, hide_border_and_title=False, show_raw=True):
    header_names = ["time"]
    if fieldnames is not None:
        for field in fieldnames:
            if field != '_stored':
                header_names.append(str(field))
    header_names += ["RAW"]
    data = []
    table = AsciiTable(data, "Hits")
    if hide_border_and_title:
        table.title = None
        table.inner_heading_row_border = False
        table.outer_border = False
        table.inner_column_border = False
    else:
        data.append(header_names)

    n = len(data)

    for hit in hits:
        # first add time
        data_array = [format_time_value(hit["timeInSeconds"])]
        hit_fields = hit["payload"]["fields"]

        data.append(data_array)
        if fieldnames is not None:
            for field in fieldnames:
                if field != '_stored':
                    val = None
                    if field in hit_fields.keys():
                        val = hit_fields[field]
                    if val is not None and len(val) > 0:
                        hl = get_hl_field_entities(hit, field)
                        field_val = highlight_str(val[0], hl[0]) if hl else val[0]
                        data_array.append(field_val)
                    else:
                        data_array.append("n/a")
        if show_raw:
            data_array.append("n/a")

    if show_raw:
        for hit in hits:
            raw_val = raw_payload(hit)
            if raw_val is not None:
                hl = get_hl_stored_entities(hit)
                if hl:
                    raw_val = highlight_str(raw_val, hl)
                max_width = table.column_max_width(len(header_names) - 1)
                try:
                    wrapped_string = '\n'.join(wrap(raw_val, max_width))
                except ValueError:
                    wrapped_string = raw_val
                data[n][len(header_names) - 1] = wrapped_string
            n = n + 1

    if len(data) > 0:
        print(table.table)


def print_schema(name, resp):
    header_names = ["column", "type"]
    data = [header_names]
    title = "{}:{} rows".format(name, resp["numDocs"])
    table = AsciiTable(data, title)

    schema = resp["schema"]
    if schema is not None:
        for field in schema["fields"]:
            field_name = field["name"]
            if field["isKey"]:
                col_type = "key"
            elif field["isMeta"]:
                col_type = "meta"
            elif field["isNumeric"]:
                col_type = "numeric"
            else:
                col_type = "text"

            data.append([field_name, col_type])
        print(table.table)
    else:
        print("table: {} not found".format(name))
        print("problem fetching schema for table: \"{}\"".format(name))


def print_cluster(name, overview_info):
    if name is None or len(name) == 0:
        print("tables: [{}]".format(",".join(overview_info.keys())))
        for table_name in overview_info.keys():
            print_table_info(table_name, overview_info[table_name])
    else:
        if name in overview_info:
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
