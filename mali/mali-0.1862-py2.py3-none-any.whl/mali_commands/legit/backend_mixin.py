# coding=utf-8
from .connection_mixin import ConnectionMixin


class BackendMixin(ConnectionMixin):
    def __init__(self, connection, config, handle_api):
        self.__volume_id = connection.data_volume_config.volume_id
        self.__config = config
        self.__handle_api = handle_api
        super(BackendMixin, self).__init__(connection)

    @property
    def _config(self):
        return self.__config

    @property
    def _handle_api(self):
        return self.__handle_api

    @property
    def _volume_id(self):
        return self.__volume_id
