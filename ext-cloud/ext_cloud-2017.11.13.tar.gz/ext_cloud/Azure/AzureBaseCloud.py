class AzureBaseCloudcls:

    def __init__(self, **kwargs):
        self._credentials = {}
        self._name = None
        self._id = None
        slef._azure_ref = None

        if 'name' in kwargs:
            self._name = kwargs['name']
        if 'id' in kwargs:
            self._id = kwargs['id']
        if 'credentials' in kwargs:
            self._credentials = kwargs['credentials']

    @property
    def name(self):
        return self._name

    @property
    def id(self):
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
