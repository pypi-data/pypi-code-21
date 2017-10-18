#!/bin/env python

"""Migrate all the Kibana Dashboards from SOURCE_HOST to DEST_HOST, including the visualizations.

This script may be run repeatedly, but any dashboard changes on
DEST_HOST will be overwritten if so.

"""

import urllib
import json
import sys
from pprint import pprint

import requests


def http_post(url, data):
    response = requests.post(url=url,
                             verify=False,
                             data=data)
    return response.text


def http_put(url, data):
    response = requests.put(url=url,
                            verify=False,
                            data=data)
    return response


def copy_kibana_dashboard_and_visualizations(version, source_host, destination_host):

    kibana_index_dict = {3: "kibana-int",
                         4: ".kibana-4"}  # might be .kibana-4
    index_list = ['"dashboard"', '"visualization"']

    kibana_index = kibana_index_dict[version]

    old_dashboards_url = "https://%s/%s/_search" % (source_host, kibana_index)

    for index in index_list:

        old_dashboards_query = ("""{
           size: 9999,
           query: { filtered: { filter: { type: { value: %s } } } } }
        }""" % index)

        try:
            old_dashboards_results = json.loads(http_post(old_dashboards_url, old_dashboards_query))
            old_dashboards_raw = old_dashboards_results['hits']['hits']
        except exception as e:
            print "couldn't get index from ES"
            sys.exit(1)

        old_dashboards = {}
        for doc in old_dashboards_raw:
            old_dashboards[doc['_id']] = doc['_source']
            print(doc['_source'])
        for dash_id, dashboard in old_dashboards.items():
            # Remove the quote when creating the URL
            index = index.strip('"')
            kibana_index = ".kibana-4"
            put_url = "https://%s/%s/%s/%s" % (destination_host, kibana_index, index, urllib.quote(dash_id))
            print(http_put(put_url, json.dumps(dashboard)))


if __name__ == '__main__':

    source = "localhost:8551"
    destination = "localhost:8555"
    # KIBANA_VERSION = 3
    KIBANA_VERSION = 4

    copy_kibana_dashboard_and_visualizations(KIBANA_VERSION, source, destination)
