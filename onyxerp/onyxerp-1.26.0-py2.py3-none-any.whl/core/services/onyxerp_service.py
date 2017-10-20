class OnyxErpService(object):

    __api_root = str()
    __app = object()

    def get_api_root(self):
        return self.__api_root

    def set_api_root(self, api_root):
        self.__api_root = api_root
        return self

    def get_app(self):
        return self.__app

    def set_app(self, app: object):
        self.__app = app
        return self
