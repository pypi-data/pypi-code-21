from ext_cloud.OpenStack.utils.OpenStackClients import OpenStackClientFactory


class OpenStackBaseCloudcls():

    def __init__(self, **kwargs):
        self._credentials = None
        self._name = None
        self._id = None
        self._clients = None

        if 'name' in kwargs:
            self._name = kwargs['name']
        if 'id' in kwargs:
            self._id = kwargs['id']
        if 'credentials' in kwargs:
            import collections
            self._credentials = collections.defaultdict(lambda: None, kwargs['credentials'])
            if 'cacert' not in self._credentials:
                self._credentials['cacert'] = None

    @property
    def name(self):
        return self._name

    @property
    def oid(self):
        return self._id

    def __repr__(self):
        ret = ""
        for varible in dir(self):
            if not varible.startswith("_") and isinstance(getattr(self.__class__, varible), property):
                value = getattr(self, varible)
                if value is None:
                    value = "None"
                if not isinstance(value, str):
                    value = str(value)
                ret = ret + varible + ":" + value + "  "
        return ret

    def obj_to_dict(self):
        dic = {}
        for varible in dir(self):
            if not varible.startswith("_") and isinstance(getattr(self.__class__, varible), property):
                value = getattr(self, varible)
                if value is None:
                    value = "None"
                if not isinstance(value, str):
                    value = str(value)

                dic[varible] = value
        return dic

    def list_metrics(self):
        return []

    @property
    def _Clients(self):
        return self._Clients

    @_Clients.getter
    def _Clients(self):
        if self._clients is None:
            self._clients = OpenStackClientFactory().get(**self._credentials)
        return self._clients
