from .api.app import get_app_list


class App(object):
    """
    Steam App Service
    """

    def __init__(self):
        pass

    @classmethod
    def list(cls):
        """
        Gets the complete list of public apps.

        :return: List
        """
        res = get_app_list()
        app_list = res['applist']

        return app_list['apps']