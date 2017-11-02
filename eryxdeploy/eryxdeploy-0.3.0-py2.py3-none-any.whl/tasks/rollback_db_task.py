from fabric.tasks import Task


class RollbackDBTask(Task):
    """
    NOTE: Untested. Use at your own risk!
    """

    name = 'rollback_db'

    def __init__(self, app_stack):
        self._app_stack = app_stack
        super(RollbackDBTask, self).__init__()

    def run(self):
        self._app_stack.rollback_db_to_latest_backup()
