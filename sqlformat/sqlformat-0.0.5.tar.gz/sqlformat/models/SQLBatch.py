
class SQLBatch:
    def __init__(self, storage_strategy, buffer_strategy):
        self._reset()
        self.storage_strategy = storage_strategy
        self.buffer_strategy = buffer_strategy

    def _reset(self):
        self._statements = []
        self.result_should_persistence = False

    def result_persistence(self, destination):
        self._statements = []
        self.add_sql(self.buffer_strategy.create_buffer())
        self.buffer_strategy.buffer_destination = destination
        self.result_should_persistence = True

    def add_procedure(self, procedure_path, procedure_variables: dict = {}):
        if self.result_should_persistence:
            procedure_variables = self._set_temp_table_for_persistence_result(procedure_variables)
        self._statements += self.storage_strategy.parse_procedure(procedure_path, procedure_variables)

    def _set_temp_table_for_persistence_result(self, procedure_variables):
        keyword_variables = procedure_variables.get('keyword', {})
        keyword_variables.setdefault('temp_table', self.buffer_strategy.buffer_id)
        if not 'keyword' in procedure_variables:
            procedure_variables['keyword'] = keyword_variables
        return procedure_variables

    def add_sql(self, sql):
        self._statements.append(sql)

    def get_statements(self):
        if self.result_should_persistence:
            self.add_sql(self.buffer_strategy.flush_buffer())
            statements = self._statements
            return statements
        else:
            return self._statements


