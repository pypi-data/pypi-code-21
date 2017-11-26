class SQLStatement:
    def __init__(self, statement):
        self.statement = statement
        self.is_latest_statement = False

    def format(self, *args, **kwargs):
        self.statement = self.statement.format(*args, **kwargs)
        return self.statement
