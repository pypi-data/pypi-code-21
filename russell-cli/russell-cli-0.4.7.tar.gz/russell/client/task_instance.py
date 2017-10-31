from russell.client.base import RussellHttpClient
from russell.model.task_instance import TaskInstance


class TaskInstanceClient(RussellHttpClient):
    """
    Client to interact with TaskInstance api
    """
    def __init__(self):
        self.url = "/taskinstances/"
        super(TaskInstanceClient, self).__init__()

    def get(self, id):
        task_instance_dict = self.request("GET",
                                "{}{}".format(self.url, id))
        ti = TaskInstance.from_dict(task_instance_dict)
        return ti
