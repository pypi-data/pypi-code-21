# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

""" Agent Module handles communication and instrumentation, this
is the main class.
"""

from __future__ import unicode_literals
from __future__ import print_function
from collections import defaultdict
from ..sensor_events import DiscoveryEvent
from json import JSONEncoder


def inner_dict(next):
    return lambda: defaultdict(next)


class DataExfilRule(object):
    def __init__(self):
        self.body_event = False
        self.body_redact = False
        self.body_hash = False
        self.log_event = False
        self.log_redact = False
        self.log_hash = False
        self.id = 0


class DatabaseFieldEndpoint(dict):
    def __init__(self):
        self.discovered = False
        self.data_exfil_rule = None


class RouteEndpoint(object):
    def __init__(self):
        self.discovered = False
        # self.database_fields = inner_dict(inner_dict(inner_dict(inner_dict(DatabaseFieldEndpoint))))()
        self.database_fields = inner_dict(DatabaseFieldEndpoint)()
        self.database_exfil_rules = inner_dict(inner_dict(inner_dict(inner_dict(DatabaseFieldEndpoint))))()

    def hash_database_tuple(self, database, schema, table, fields):
        return hash(database + "," + schema + "," + table + "," + ",".join(fields))

    def has_field_been_discovered(self, database, schema, table, field):
        return self.have_fields_been_discovered(database, schema, table, [field])

    def have_fields_been_discovered(self, database, schema, table, fields):
        if (database and schema and table and fields):
            if (self.database_fields[self.hash_database_tuple(database, schema, table, fields)].discovered == False):
                return True
        return False

    def set_field_discovered(self, database, schema, table, field):
        self.set_fields_discovered(database, schema, table, [field])

    def set_fields_discovered(self, database, schema, table, fields):
        if (database and schema and table and fields):
            self.database_fields[self.hash_database_tuple(database, schema, table, fields)].discovered = True


class RouteTable(object):
    def __init__(self):
        self.routes = defaultdict(RouteEndpoint)
        self.update_cache_flag = False
        # self.full_database = DiscoveryEndpoint()
