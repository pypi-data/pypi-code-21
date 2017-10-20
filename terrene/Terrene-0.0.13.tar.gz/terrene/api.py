from .config import api
import coreapi


class CoreAPI:
    client = None
    document = None

    def __init__(self, client=None, document=None):
        if client is None and document is None:
            self.client = coreapi.Client()
            self.document = self.client.get(api() + '/schema/')
        else:
            self.client = client
            self.document = document


class CoreAPIMixin:
    def act(self, namespace, params):
        return self.coreapi.client.action(
            self.coreapi.document, self.namespace + namespace, params=params,
            validate=False)


class BaseModel(CoreAPIMixin):
    _data = {}
    coreapi = None
    namespace = []
    credentials = None

    def __init__(self, object_id, namespace, coreapi, credentials=None):
        self._data['object_id'] = object_id
        self.namespace = namespace
        self.coreapi = coreapi
        self.credentials = credentials
        self.retrieve()

    def pre_retrieve(self):
        pass

    def retrieve(self):
        self.pre_retrieve()
        self._data = self.act(['read'], {'object_id': self._data['object_id']})
        self.post_retrieve()

    def post_retrieve(self):
        pass

    def pre_save(self):
        pass

    def save(self):
        self.pre_save()
        self.act(['partial_update'], self._data)
        self.post_save()

    def post_save(self):
        pass

    def pre_delete(self):
        pass

    def delete(self):
        self.pre_delete()
        self.act(['delete'], {'object_id': self.object_id})
        self.post_delete()

    def post_delete(self):
        pass

    def __getattr__(self, item):
        try:
            return self._data[item]
        except KeyError:
            raise AttributeError

    def __setattr__(self, key, value):
        if self._data.get(key, None) is not None:
            self._data[key] = value
        else:
            super(BaseModel, self).__setattr__(key, value)

    def __str__(self):
        from beeprint import pp
        return pp(self._data, output=False)


class BaseModelManager(CoreAPIMixin):
    # public attributes
    coreapi = None
    credentials = None
    model = BaseModel
    namespace = []

    def __init__(self, *args, **kwargs):
        self.credentials = kwargs.pop('credentials', None)

        # retrieve the authenticated coreapi schema
        if self.credentials is not None:
            self.coreapi = self.credentials.coreapi
        else:
            self.coreapi = CoreAPI()

    def query(self, query_params):
        objs = []
        for obj in self.act(['list'], query_params)['results']:
            objs.append(self.model(
                obj['object_id'], self.namespace, self.coreapi, self.credentials))
        return objs

    def get(self, object_id):
        return self.model(object_id, self.namespace, self.coreapi, self.credentials)

    def pre_create(self, **params):
        return params

    def create(self, **params):
        params = self.pre_create(**params)
        results = self.model(
            self.act(['create'], params)['object_id'], self.namespace,
            self.coreapi, self.credentials)
        return self.post_create(results)

    def post_create(self, results):
        return results
