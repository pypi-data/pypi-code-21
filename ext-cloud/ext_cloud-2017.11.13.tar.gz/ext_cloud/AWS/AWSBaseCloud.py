class AWSBaseCloudcls:

    def __init__(self, **kwargs):
        self._credentials = {}
        if 'name' in kwargs:
            self._name = kwargs['name']
        if 'id' in kwargs:
            self._id = kwargs['id']
        if 'credentials' in kwargs:
            self._credentials = kwargs['credentials']

        if 'auth_url' not in self._credentials:
            self._credentials['auth_url'] = 'https://aws.amazon.com/'

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

    def addtag(self, name, value):
        self._aws_ref.add_tag(name, value)

    def gettags(self):
        return self._aws_ref.tags
