from dateutil.parser import parse
import pypyodbc
import json

from hivemindplus.consts import KEY_PREFIX
from hivemindplus.exceptions import AgreementNotReachedException


class ResultProcessor:
    def __init__(self, config, task_id):
        self._config = config
        self._task_id = task_id

    def process(self, api):
        if not self._config:
            return

        self._verify_config(api)

        connection = pypyodbc.connect(self._config.connection_string)

        self._create_iteration_table_if_not_exists(connection)
        self._create_instance_table_if_not_exists(connection)

        results = api.get_results()
        stored_keys = self._get_stored_result_instance_keys(connection)
        filtered_results = [result for result in results if self._get_instance_key(result) not in stored_keys]

        self._process_iteration_results(connection, filtered_results)
        self._process_instance_results(connection, filtered_results, api)

        connection.close()

    def _verify_config(self, api):
        task = api.get_task()
        if task['targetAgreement'] and self._config.agreement_enabled:
            print('***WARNING***: Automated agreement checking is enabled in Hivemind as well as custom agreement '
                  'checking in Hivemind Plus')

    def _create_iteration_table_if_not_exists(self, connection):
        table = self._get_iteration_table()
        print('Creating iteration table {} if it does not already exist'.format(table))

        sql = """
        IF OBJECT_ID(N'{0}', N'U') IS NULL
        CREATE TABLE {0} (
            IterationId INT          NOT NULL PRIMARY KEY,
            InstanceKey VARCHAR(200) NOT NULL,
            InstanceId  INT          NOT NULL,
            TaskId      INT          NOT NULL,
            WorkerId    VARCHAR(200) NOT NULL,
            Result      VARCHAR(MAX) NOT NULL,
            Error       BIT          NOT NULL,
            Start       DATETIME2    NOT NULL,
            Finish      DATETIME2    NOT NULL
        )
        """.format(table)

        cursor = connection.cursor()
        cursor.execute(sql)
        cursor.commit()
        cursor.close()

    def _create_instance_table_if_not_exists(self, connection):
        table = self._get_instance_table()
        print('Creating instance table {} if it does not already exist'.format(table))

        sql = """
        IF OBJECT_ID(N'{0}', N'U') IS NULL
        CREATE TABLE {0} (
            InstanceKey VARCHAR(200) NOT NULL PRIMARY KEY,
            InstanceId INT           NOT NULL,
            TaskId     INT           NOT NULL,
            Result     VARCHAR(MAX)  NOT NULL,
            Error      BIT           NOT NULL
        )
        """.format(table)

        cursor = connection.cursor()
        cursor.execute(sql)
        cursor.commit()
        cursor.close()

    def _process_iteration_results(self, connection, results):
        table = self._get_iteration_table()
        print('Loading new iteration results into {}'.format(table))

        cursor = connection.cursor()

        for result in results:
            instance_id = result['instanceId']
            instance_key = self._get_instance_key(result)

            if instance_key is None:
                # Result not managed by hivemind-plus
                continue

            for iteration_result in result['iterationResults']:
                iteration_id = iteration_result['iterationId']
                worker_id = iteration_result['worker']
                result_data = json.dumps(iteration_result['data'])
                error = iteration_result['isError']
                start = parse(iteration_result['start'])
                end = parse(iteration_result['end'])

                sql = """
                IF NOT EXISTS (SELECT 1 FROM {0} WHERE IterationId = {1})
                INSERT INTO {0}(IterationId, InstanceKey, InstanceId, TaskId, WorkerId, Result, Error, Start, Finish)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
                """.format(table, iteration_id)

                cursor.execute(sql, (iteration_id, instance_key, instance_id, self._task_id, worker_id, result_data, error, start, end))
                cursor.commit()

        cursor.close()

    def _process_instance_results(self, connection, results, api):
        table = self._get_instance_table()
        print('Loading new instance results into {}'.format(table))

        cursor = connection.cursor()

        for result in results:
            instance_key = self._get_instance_key(result)
            instance_id = result['instanceId']

            if self._result_invalid_for_processing(instance_key, result):
                continue

            if self._config.agreement_enabled:
                try:
                    agreement_summary = self._apply_custom_agreement(result, api)
                    result_obj = agreement_summary.result

                    # If we use the agreement function, also submit the feedback to Hivemind
                    self._submit_feedback(api, instance_id, agreement_summary.correct_iterations, True)
                    self._submit_feedback(api, instance_id, agreement_summary.incorrect_iterations, False)

                except AgreementNotReachedException:
                    continue
            else:
                result_obj = result['result']

            result_data = json.dumps(result_obj['data'])
            error = result_obj['isError']

            sql = 'INSERT INTO {}(InstanceKey, InstanceId, TaskId, Result, Error) VALUES(?, ?, ?, ?, ?)'.format(table)

            try:
                cursor.execute(sql, (instance_key, instance_id, self._task_id, result_data, error))

                if self._config.output_function:
                    self._config.output_function(result_obj)

                cursor.commit()
            except Exception as e:
                print('Exception encountered whilst trying to process agreed result for key={}'.format(instance_key))
                print(str(e))
                cursor.rollback()

            # Execute the feedback function now if there is one
            if self._config.feedback_function:
                self._config.feedback_function(result_obj, result["iterationResults"])

        cursor.close()

    def _apply_custom_agreement(self, result, api):
        instance_id = result['instanceId']
        iteration_results = result['iterationResults']
        instance_key = self._get_instance_key(result)

        if len(iteration_results) == 0:
            raise Exception("No iteration results available. Not calling agreement function.")

        try:
            if self._config.agg_agreement_function:
                return AgreementSummary(self._config.agg_agreement_function(iteration_results, instance_id))
            else:
                return self._apply_agreement_function(iteration_results)
        except AgreementNotReachedException:
            # Attempt reiteration
            if self._config.max_iterations > len(iteration_results):
                print('Agreement not reached for key={}, reiterating instance'.format(instance_key))
                api.reiterate(instance_id)
            raise AgreementNotReachedException()

    def _apply_agreement_function(self, iteration_results):
        if len(iteration_results) == 0:
            raise AgreementNotReachedException()

        fn = self._config.agreement_function
        target = self._config.target_agreement

        agreements = []

        for result in iteration_results:
            matched = False
            for bucket in agreements:
                if fn(result, bucket.result):
                    bucket.add(result)
                    matched = True
                    break

            if not matched:
                agreements.append(ResultBucket(result))

        # Sort the agreements buckets by how large they are
        agreements.sort(key=lambda x: x.count(), reverse=True)

        agreed_bucket = agreements[0]

        if (agreed_bucket.count() / len(iteration_results)) >= target:
            # Collect the remaining iterationIds that are incorrect
            remaining_iterations = [item for sublist in agreements[1:] for item in sublist]
            return AgreementSummary(agreed_bucket.result, agreed_bucket.iterationIds, remaining_iterations)
        else:
            raise AgreementNotReachedException()

    def _result_invalid_for_processing(self, instance_key, result):
        agreement_not_reached = result['result'] is None and not self._config.agreement_enabled
        not_managed_by_hivemind_plus = instance_key is None
        incomplete = result['status'] != 'Complete'

        return agreement_not_reached or not_managed_by_hivemind_plus or incomplete

    def _get_stored_result_instance_keys(self, connection):
        sql = 'SELECT InstanceKey FROM {}'.format(self._get_instance_table())
        cursor = connection.cursor()
        cursor.execute(sql)
        keys = {row[0] for row in cursor.fetchall()}
        cursor.close()
        return keys

    def _get_instance_table(self):
        if self._config.instance_table is None:
            return 'dbo.Task_{}_InstanceResults'.format(self._task_id)
        else:
            return self._config.instance_table

    def _get_iteration_table(self):
        if self._config.iteration_table is None:
            return 'dbo.Task_{}_IterationResults'.format(self._task_id)
        else:
            return self._config.iteration_table

    def _get_instance_key(self, result):
        tags = result['tags']
        key_tag = next((tag for tag in tags if tag.startswith(KEY_PREFIX)), None)
        return key_tag[len(KEY_PREFIX):] if key_tag is not None else None

    def _submit_feedback(self, api, instance_id, iteration_ids, is_correct):
        for i in iteration_ids:
            api.submit_feedback(instance_id, i, is_correct)


class ResultBucket:
    def __init__(self, result):
        self.result = {'data': result['data'], 'isError': result['isError']}
        self.iterationIds = [result['iterationId']]

    def add(self, result):
        self.iterationIds.append(result['iterationId'])

    def count(self):
        return len(self.iterationIds)


class AgreementSummary:
    def __init__(self, result, correct_iterations=[], incorrect_iterations=[]):
        self.incorrect_iterations = incorrect_iterations
        self.correct_iterations = correct_iterations
        self.result = result

