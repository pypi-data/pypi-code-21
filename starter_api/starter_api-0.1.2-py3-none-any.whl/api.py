from starter_api.private_api import PrivateApi

"""
:type: PrivateApi
"""
__obj_starter_api = None


def init(server_host_and_port):
    """
    Init by server url
    Example: http://starter-server.localhost:28341

    :param server_host_and_port: string
    """
    global __obj_starter_api
    __obj_starter_api = PrivateApi(api_url=server_host_and_port)


def build_submit(service_id, data=None):
    """
    Build and submit task to server
    :param service_id: string
    :param data: dict
    :return: dict
    """
    return submit(
        build_task(service_id, data)
    )


def submit(task):
    """
    :type task: Task
    """
    return __obj_starter_api.submit(task)


def build_task(service_id, data=None):
    return Task(service_id, data)


class Task:
    serviceId = None
    data = {}

    def __init__(self, service_id, data=None):
        self.serviceId = service_id
        if data:
            self.data = data
