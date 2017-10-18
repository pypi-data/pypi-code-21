# coding=utf-8
import json
import uuid
from .connection_mixin import ConnectionMixin


class BigQueryOperationError(Exception):
    pass


class BigQueryMixin(ConnectionMixin):
    @classmethod
    def handle_bq_errors(cls, async_job):
        errors = async_job.errors

        if not errors:
            return

        error_msg = json.dumps(errors)

        raise BigQueryOperationError(error_msg)

    def _query_async(self, query, query_parameters=(), use_legacy_sql=False):
        query_id = str(uuid.uuid4())

        bq_client = self._connection

        query_job = bq_client.run_async_query(query_id, query, query_parameters=query_parameters)
        query_job.use_legacy_sql = use_legacy_sql

        return query_job

    def _query_sync(self, query, query_parameters=(), use_legacy_sql=False, process_row=None):
        query_job = self._query_async(query, query_parameters, use_legacy_sql=use_legacy_sql)
        query_job.begin()
        self.handle_bq_errors(query_job.result())

        destination_table = query_job.destination
        destination_table.reload()

        for result in destination_table.fetch_data():
            if not process_row:
                yield result
                continue

            yield process_row(result, query_job)
