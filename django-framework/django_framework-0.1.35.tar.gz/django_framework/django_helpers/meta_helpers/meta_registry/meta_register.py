

from django_framework.django_helpers.register_helpers import Registry

instance = None

class MetaRegistry(Registry):
    REGISTRY_TYPE = 'Meta'
    REGISTER = {}
    
    SHOULD_CHECK_TYPE = True
    
    @classmethod
    def set_instance(cls):
        if instance == None:
            global instance
            instance = MetaRegistry()


def register_meta(cls):
    MetaRegistry.set_instance()
    instance.register(cls = cls)

def get_meta(meta_name): # converts string to cls
    return instance.get(name = meta_name)
    
def get_meta_name(meta): # converts cls to a string
    return instance.get_name(cls = meta)

def get_meta_name_list(): # converts cls to a string
    return instance.get_name_list()

