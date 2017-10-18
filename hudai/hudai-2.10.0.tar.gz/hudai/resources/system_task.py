"""
hudai.resources.system_task
"""
from datetime import datetime

from ..helpers.resource import Resource
from ..helpers.http_errors import api_404


class SystemTaskResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/system-tasks')
        self.resource_name = 'SystemTask'

    def list(self,
             page=None,
             started_after=None,
             started_before=None,
             completed=None,
             task_id=None):
        """
        Lists the existing system tasks, filtered by the given keyword args
        """
        return self._list(
            task_id=task_id,
            page=page,
            started_after=started_after,
            started_before=started_before,
            completed=completed)

    def create(self,
               task_id=None,
               attempts=None,
               started_at=None,
               completed_at=None):
        """
        Creates a new system task
        """
        return self._create(
            task_id=task_id,
            attempts=attempts,
            started_at=started_at,
            completed_at=completed_at)

    def fetch(self, entity_id):
        """
        Retrieves the task by its API id
        """
        return self._fetch(entity_id)

    def fetch_by_task_id(self, task_id):
        """
        Retrieves the task using its celery id
        """
        tasks = self._list(task_id=task_id).get('rows', [])
        return tasks[0] if tasks else api_404()

    def update(self,
               entity_id,
               attempts=None,
               started_at=None,
               completed_at=None):
        """
        Update the task's started_at or completed_at
        """
        return self._update(entity_id,
                            attempts=attempts,
                            started_at=started_at,
                            completed_at=completed_at)

    def mark_complete(self, entity_id, completed_at=datetime.now()):
        """
        Marks the task as complete (defaults to completed now)
        """
        return self._update(entity_id, completed_at=completed_at)

    def delete(self, entity_id):
        """
        Removes the task entry
        """
        return self._delete(entity_id)
