class Version(object):
    def __init__(self, version_code, comment, sql_text, before_migrate=None):
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
        self.sql_text = sql_text
        self.comment = comment
        self.before_migrate = before_migrate

    def __repr__(self):
        return f"<Version {self.version_code} - {self.comment}>"
