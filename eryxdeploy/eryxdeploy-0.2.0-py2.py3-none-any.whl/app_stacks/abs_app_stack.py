class AppStack(object):
    def install(self):
        raise NotImplementedError("Subclass responsibility.")

    def upgrade(self):
        raise NotImplementedError("Subclass responsibility.")

    def rollback_db_to_latest_backup(self):
        raise NotImplementedError("Subclass responsibility.")
