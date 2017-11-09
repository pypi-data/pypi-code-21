from django_framework.django_helpers.register_helpers import Registry

instance = None
class APIRegistry(Registry):
    REGISTRY_TYPE = 'API'
    REGISTER = {}
    
    @classmethod
    def set_instance(cls):
        if instance == None:
            global instance
            instance = APIRegistry()


def register_api(cls):
    APIRegistry.set_instance()
    instance.register(cls = cls)
    

def get_api(api_name): # converts string to cls
    return instance.get(name = api_name)
    
def get_api_name(api): # converts cls to a string
    return instance.get_name(cls = api)

def get_api_name_list(): # converts cls to a string
    return instance.get_name_list()



