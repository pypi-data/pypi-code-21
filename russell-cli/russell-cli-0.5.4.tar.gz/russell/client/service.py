from russell.client.base import RussellHttpClient
from russell.model.service import Service
from russell.log import logger as russell_logger


class ServiceClient(RussellHttpClient):
    """
    Client to get service status from the server
    """
    def __init__(self):
        self.url = "/service_status"
        super(ServiceClient, self).__init__()

    def get_service_status(self):
        data_dict = self.request("GET", self.url)
        russell_logger.debug("Service status info :{}".format(data_dict))
        return Service.from_dict(data_dict)

