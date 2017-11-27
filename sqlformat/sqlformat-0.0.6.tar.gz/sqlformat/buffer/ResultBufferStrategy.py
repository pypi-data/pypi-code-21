import uuid

from sqlformat.models.SQLStatement import SQLStatement


class ResultBufferStrategy:
    """
    Class default do nothing.
    """

    def __init__(self):
        self.change_buffer_id()
        self.buffer_destination = None

    def change_buffer_id(self):
        self.buffer_id = uuid.uuid4()

    def create_buffer(self):
        self.change_buffer_id()
        return self._init_buffer()

    def _init_buffer(self):
        return SQLStatement("""
CREATE TEMP TABLE {temp_table} (
    value STRING,
    meta1 STRING
);""".format(temp_table=self.buffer_id))

    def flush_buffer(self):
        return SQLStatement("UNLOAD {temp_table} TO {destination};".format(
            temp_table=self.buffer_id,
            destination=self.buffer_destination
        ))
