

instance = None

from django_framework.django_helpers.register_helpers import Registry

class SerializerRegistry(Registry):
    REGISTRY_TYPE = 'Serializer'
    REGISTER = {}
    
    SHOULD_CHECK_TYPE = True
    
    @classmethod
    def set_instance(cls):
        if instance == None:
            global instance
            instance = SerializerRegistry()


def register_serializer(cls, version = None):
    SerializerRegistry.set_instance()
    instance.register(cls = cls)

def get_serializer(serializer_name, version = 'default'): # converts string to cls
    
    if version == 'admin':
        if serializer_name.find(version) < 0:
            serializer_name = 'admin_' + serializer_name
    return instance.get(name = serializer_name)
    
def get_serializer_name(serializer): # converts cls to a string
    return instance.get_name(cls = serializer)

def get_serializer_name_list(): # converts cls to a string
    return instance.get_name_list()




#   
# import collections
# registry = collections.defaultdict(dict)
#   
# def register_serializer(cls, version=None):
#     if version == None:
#         version = 'default'
#       
#     class_name = cls.__name__
#     if registry[version].get(class_name) == None:
#         registry[version][class_name] = cls
#     else:
#         return
#         raise NameError('The class you are trying to register is already in!...')
#       
#     print(registry)
#       
# def get_serializer(serializer = None, serializer_name = None, serializer = None, version = None):
#   
#     if serializer:
#         serializer = serializer + 'Serializer'
#     elif serializer_name:
#         serializer = serializer_name
#       
#       
#   
#     if version == None:
#         version = 'default'
#           
#           
#     serializer = registry.get(version, {}).get(serializer)
#     if serializer == None:
#         raise AttributeError('You have not properly registered this serializer name, or this name does not exist.')
#       
#     return serializer
#   
#   
# def get_serializer_name(serializer = None, serializer_name = None):
#     if serializer == None and serializer_name == None:
#         raise ValueError('Need to specify a serializer/serializer_name!')
#       
#     if serializer == None and serializer_name != None:
#         serializer = serializer_name
#       
#       
#     serializer_name = serializer.__name__ if hasattr(serializer, "__name__") else serializer.__class__.__name__
#       
#     return serializer_name