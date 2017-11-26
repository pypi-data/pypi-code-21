from abc import ABC, abstractmethod
import json

from sqlformat.models.SQLStatement import SQLStatement


class StorageStrategyTemplate(ABC):

    def parse_procedure(self, procedure_path, procedure_variables: dict):
        """
        To download procedure from storage and transform placeholder with value
        """
        procedure_statements = self.get_procedure_statements(procedure_path)
        procedure_variables_keyword = procedure_variables.get('keyword', {})
        procedure_variables_index = procedure_variables.get('index', [])
        for sql_statement in procedure_statements:
            sql_statement.format(*procedure_variables_index, **procedure_variables_keyword)
        return procedure_statements

    def get_procedure_statements(self, procedure_path):
        """
        To download procedure from storage
        """
        content = self._read_procedure(procedure_path)
        sql_procedure = json.loads(content)
        statements = []
        for sql_file in sql_procedure:
            sql_file_content = self._read_sql(sql_file["file"])
            statements+= self.split_statements(sql_file_content)
        return statements

    def split_statements(self, sql_file_content):
        statements = []
        file_statements = sql_file_content.split(";\n")
        for index, file_statement in enumerate(file_statements):
            file_statement = file_statement.strip()
            is_latest_statement = index == len(file_statements) - 1
            if not file_statement.endswith(';'):
                file_statement = file_statement + ';'
            statement = SQLStatement(file_statement)
            statement.is_latest_statement = is_latest_statement
            statements.append(statement)
        return statements

    @abstractmethod
    def _read_procedure(self, procedure_path):
        pass

    @abstractmethod
    def _read_sql(self, sql_path):
        pass
