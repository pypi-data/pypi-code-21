from collections import OrderedDict

from django.core import serializers


class OnyxErpService(object):

    __api_root = str()
    __app = object()

    def get_api_root(self):
        """

        :return: str
        """
        return self.__api_root

    def set_api_root(self, api_root):
        """

        :param api_root:
        :return:
        """
        self.__api_root = api_root
        return self

    def get_app(self):
        """

        :return:
        """
        return self.__app

    def set_app(self, app: object):
        """

        :param app:
        :return:
        """
        self.__app = app
        return self

    def deserialize_cached_model(self, key: str(), cached_data: str()) -> object:
        """

        :param key:
        :param cached_data:
        :return:
        """
        try:
            for model in cached_data:
                retorno = OrderedDict()
                retorno[key] = model['pk']
                retorno.update(model['fields'])
                return retorno
        except Exception:
            self.__app['log'].warning(
                "Falha ao deserializar arquivo de cache em model. Data: %s" % str(cached_data),
                exc_info=True
            )
            return False
