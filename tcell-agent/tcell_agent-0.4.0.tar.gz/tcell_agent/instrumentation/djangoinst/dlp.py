# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

import logging
from logging import Logger
import itertools

from collections import defaultdict

from tcell_agent.agent import TCellAgent, PolicyTypes
from tcell_agent.appsensor.django import django_meta
from tcell_agent.config import CONFIGURATION
from tcell_agent.instrumentation.djangoinst.middleware.globalrequestmiddleware import GlobalRequestMiddleware
from tcell_agent.instrumentation.manager import InstrumentationManager

from .. import safe_wrap_function

try:
    from django.db.models.expressions import Col

    col_supported = True
except:
    col_supported = False

logger = logging.getLogger('tcell_agent').getChild(__name__)


def check_appsensor_max_db_rows(request, total_records, appsensor_policy):
    if appsensor_policy:
        appsensor_meta = django_meta(request)
        appsensor_policy.check_db_rows(appsensor_meta, total_records)


def check_dlp_max_records(request, total_records, dataloss_policy):
    if dataloss_policy and dataloss_policy.enabled and total_records > CONFIGURATION.max_data_ex_db_records_per_request:
        logger.warn("Retrieved too many records for route_id: %s", request._tcell_context.route_id)


def check_max_database_rows_reached(request, total_records, dataloss_policy, appsensor_policy):
    if request:
        safe_wrap_function(
            "Run Appfirewall's max number of DB records check",
            check_appsensor_max_db_rows,
            request,
            total_records,
            appsensor_policy)

        safe_wrap_function(
            "Run DLP's max number of DB records check",
            check_dlp_max_records,
            request,
            total_records,
            dataloss_policy)


def singlecallback(row, track_idxes, request, count):
    if count < CONFIGURATION.max_data_ex_db_records_per_request:
        if track_idxes is not None:
            for track_idx in track_idxes:
                actions, db_identifier, schema_identifier, table, column = track_idxes[track_idx]
                for action in actions:
                    try:
                        request._tcell_context.add_response_db_filter(row[track_idx], action, db_identifier,
                                                                      schema_identifier, table, column)
                    except Exception as e:
                        print(e)

    return row


def multicallback2(rows, track_idxes, request, i, process_dataloss_policy):
    number_of_rows = len(rows)
    j = i * number_of_rows - 1
    for row in rows:
        j += 1
        if process_dataloss_policy:
            singlecallback(row, track_idxes, request, j)

    return number_of_rows


def multicallback(results, track_idxes, request, dataloss_policy, appsensor_policy):
    if results:
        results, results2 = itertools.tee(results)
        total_records = 0
        process_dataloss_policy = dataloss_policy and dataloss_policy.enabled and request and len(track_idxes.keys()) > 0
        for counter, rows in enumerate(results):
            total_records += multicallback2(rows, track_idxes, request, counter, process_dataloss_policy)

        check_max_database_rows_reached(request, total_records, dataloss_policy, appsensor_policy)

        return results2

    else:
        return None


def dlp_instrumentation():
    from django.db.models.sql.compiler import SQLCompiler
    from django.db.models.sql.constants import (
        CURSOR, GET_ITERATOR_CHUNK_SIZE, MULTI, NO_RESULTS, ORDER_DIR, SINGLE,
    )

    # Django 1.5 <= 1.10 method signature
    #     def execute_sql(self, result_type=MULTI):
    # Django 1.11 method signature
    #     def execute_sql(self, result_type=MULTI, chunked_fetch=False):
    def _tcell_execute_sql(_tcell_original, self, *args, **kwargs):
        results = _tcell_original(self, *args, **kwargs)
        try:
            result_type = kwargs.get('result_type', MULTI)
            request = GlobalRequestMiddleware.get_current_request()
            dataloss_policy = TCellAgent.get_policy(PolicyTypes.DATALOSS)
            appsensor_policy = TCellAgent.get_policy(PolicyTypes.APPSENSOR)

            route_id = None
            if request:
                try:
                    route_id = request._tcell_context.route_id
                except:
                    pass

            if dataloss_policy and dataloss_policy.enabled or appsensor_policy.should_check_db_rows(route_id):
                try:
                    db_name = self.connection.get_connection_params().get("db", "n/a")
                except:
                    db_name = "n/a"

                db_identifier = getattr(self.connection, "vendor", "n/a")
                schema_identifier = db_name

                if col_supported:
                    if self.select:
                        try:
                            track_idxes = {}
                            tables_track = defaultdict(set)

                            if dataloss_policy and dataloss_policy.enabled:
                                for idx, select in enumerate(self.select):
                                    try:
                                        if isinstance(select[0], Col):
                                            table = select[0].alias
                                            column = select[0].target.column
                                            tables_track[table].add(column)
                                            if results and request:
                                                actions = dataloss_policy.get_actions_for_db_field(
                                                    db_identifier,
                                                    schema_identifier,
                                                    table,
                                                    column,
                                                    route_id)
                                                if actions:
                                                    track_idxes[idx] = (
                                                        actions,
                                                        db_identifier,
                                                        schema_identifier,
                                                        table,
                                                        column)
                                    except Exception as selectException:
                                        logger.debug(selectException)

                                if dataloss_policy.database_discovery_enabled:
                                    for table in tables_track:
                                        TCellAgent.discover_database_fields(db_identifier, schema_identifier, table,
                                                                            list(tables_track[table]), route_id)

                            if result_type == MULTI:
                                ans = multicallback(results, track_idxes, request, dataloss_policy, appsensor_policy)
                                if ans:
                                    return ans

                            if results and request and len(track_idxes.keys()) > 0 and result_type == SINGLE:
                                check_max_database_rows_reached(request, 1, dataloss_policy, appsensor_policy)
                                return singlecallback(results, track_idxes, request, 0)

                        except Exception as b:
                            logger.error("error in data-exposure mapping.")
                            logger.debug(b)
                elif self.query.select:
                    try:
                        track_idxes = {}
                        idx = 0
                        tables_track = defaultdict(set)

                        if dataloss_policy and dataloss_policy.enabled:
                            for col, _ in self.query.select:
                                try:
                                    if isinstance(col, (list, tuple)):
                                        table, column = col
                                        tables_track[table].add(column)
                                        if results and request:
                                            actions = dataloss_policy.get_actions_for_db_field(
                                                db_identifier,
                                                schema_identifier,
                                                table,
                                                column,
                                                route_id)
                                            if actions:
                                                track_idxes[idx] = (
                                                    actions,
                                                    db_identifier,
                                                    schema_identifier,
                                                    table,
                                                    column)
                                except Exception as selectException:
                                    logger.debug(selectException)
                                finally:
                                    idx = idx + 1

                            if dataloss_policy.database_discovery_enabled:
                                for table in tables_track:
                                    TCellAgent.discover_database_fields(db_identifier, schema_identifier, table,
                                                                        list(tables_track[table]), route_id)

                        if result_type == MULTI:
                            ans = multicallback(results, track_idxes, request, dataloss_policy, appsensor_policy)
                            if ans:
                                return ans

                        if results and request and len(track_idxes.keys()) > 0 and result_type == SINGLE:
                            check_max_database_rows_reached(request, 1, dataloss_policy, appsensor_policy)
                            return singlecallback(results, track_idxes, request, 0)

                    except Exception as b:
                        logger.debug("error in data-exposure mapping.")
                        logger.debug(b)
                elif self.query.default_cols:
                    try:
                        track_idxes = {}
                        opts = self.query.get_meta()
                        start_alias = self.query.get_initial_alias()
                        seen_models = {None: start_alias}
                        idx = 0
                        tables_track = defaultdict(set)

                        if dataloss_policy and dataloss_policy.enabled:
                            for field, model in opts.get_concrete_fields_with_model():
                                try:
                                    table = self.query.join_parent_model(opts, model, start_alias,
                                                                         seen_models)
                                    column = field.column
                                    tables_track[table].add(column)
                                    if results and request:
                                        actions = dataloss_policy.get_actions_for_db_field(
                                            db_identifier,
                                            schema_identifier,
                                            table,
                                            column,
                                            route_id)
                                        if actions:
                                            track_idxes[idx] = (
                                                actions,
                                                db_identifier,
                                                schema_identifier,
                                                table,
                                                column)
                                except Exception as selectException:
                                    logger.debug(selectException)
                                finally:
                                    idx = idx + 1

                            if dataloss_policy.database_discovery_enabled:
                                for table in tables_track:
                                    TCellAgent.discover_database_fields(db_identifier, schema_identifier, table,
                                                                        list(tables_track[table]), route_id)

                        if result_type == MULTI:
                            ans = multicallback(results, track_idxes, request, dataloss_policy, appsensor_policy)
                            if ans:
                                return ans

                        if results and request and len(track_idxes.keys()) > 0 and result_type == SINGLE:
                            check_max_database_rows_reached(request, 1, dataloss_policy, appsensor_policy)
                            return singlecallback(results, track_idxes, request, 0)

                    except Exception as b:
                        logger.debug("error in data-exposure mapping.")
                        logger.debug(b)
        except Exception as wrapping_exception:
            logger.debug(wrapping_exception)
            logger.debug("Could not complete data-exposure mapping.")
        return results

    InstrumentationManager.instrument(SQLCompiler, "execute_sql", _tcell_execute_sql)

    def _tcell_log(_tcell_original, self, level, msg, args, exc_info=None, extra=None):
        # Skip us...
        if self.name and self.name.startswith("tcell_agent"):
            return _tcell_original(self, level, msg, args, exc_info, extra)
        request = GlobalRequestMiddleware.get_current_request()
        if request:
            msg = request._tcell_context.filter_log_message(msg)
        return _tcell_original(self, level, msg, args, exc_info, extra)

    InstrumentationManager.instrument(Logger, "_log", _tcell_log)
