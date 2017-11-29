import json
import union

#
# Abstract Base Model
#

class BaseModel(object):
    def __init__(self, **attrs):
        for k, v in attrs.iteritems():
            self.__setattr__(k, v)

    def __repr__(self):
        return unicode('< union.%s(%s) >' % (type(self).__name__, self))

    def __str__(self):
        return self._to_json

    def __setattr__(self, k, v=None):
        super(BaseModel, self).__setattr__(k, v)

    @property
    def _to_dict(self):
        return dict((k, v) for k, v in self.__dict__.items() if not k.startswith('_'))

    @property
    def _to_json(self):
        return json.dumps(self._to_dict, sort_keys=True, indent=4)

    @classmethod
    def _new_api_client(cls):
        return union.UnionClient()

    @classmethod
    def all(cls):
        '''
        Returns multiple Union objects
        '''
        client = cls._new_api_client()
        return client.make_request(cls, 'get')

    @classmethod
    def get(cls, id):
        '''
        Look up one Union object
        '''
        client = cls._new_api_client()
        return client.make_request(cls, 'get', url_params={'id': id})

    def save(self):
        '''
        Save an instance of a Union object
        '''
        client = self._new_api_client()
        params = {'id': self.id} if hasattr(self, 'id') else {}
        action =  'patch' if hasattr(self, 'id') else 'post'
        saved_model = client.make_request(self, action, url_params=params, post_data=self._to_json)
        self.__init__(**saved_model._to_dict)


#
# Union Objects
#

class Customer(BaseModel):
    pass

class Invoice(BaseModel):
    pass

class Vendor(BaseModel):
    pass

class Bill(BaseModel):
    pass

class Order(BaseModel):
    pass

class Item(BaseModel):
    pass

class Organization(BaseModel):
    pass

class PaymentMethod(BaseModel):
    pass

class Payments(BaseModel):
    pass

class PurchaseOrder(BaseModel):
    pass

class Tax(BaseModel):
    pass
