class Version(object):
    def __init__(self, version_code, comment,
                 sql_text=None, sql_file=None,
                 before_migrate=None, after_migrate=None):
        """
        Create a version object.

        :param version_code: unique string that identifies the version, should follow the convention "v0", "v1", etc.
        :param sql_text: the sql script that will be executed during the migration
        :param comment: migration purpose.
        :param before_migrate: (optional) function that is run before the actual migration.
            Useful for "tough" migration that requires adding/deleting data before modifying database structure.
            This function has a single argument which is the session object.
        """
        self.version_code = version_code
        self.comment = comment
        self.sql_text = sql_text
        self.sql_file = sql_file
        self.before_migrate = before_migrate
        self.after_migrate = after_migrate

        # only sql_text or sql_file
        if sql_file and sql_text:
            raise Exception("sql_file and sql_text are exclusive")

    def __repr__(self):
        return f"<Version {self.version_code} - {self.comment}>"
