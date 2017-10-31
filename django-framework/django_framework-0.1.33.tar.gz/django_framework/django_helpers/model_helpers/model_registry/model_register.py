
instance = None

from django_framework.django_helpers.register_helpers import Registry

class ModelRegistry(Registry):
    REGISTRY_TYPE = 'Model'
    REGISTER = {}
    
    SHOULD_CHECK_TYPE = False
    
    @classmethod
    def set_instance(cls):
        if instance == None:
            global instance
            instance = ModelRegistry()


def register_model(cls):
    ModelRegistry.set_instance()
    instance.register(cls = cls)

def get_model(model_name): # converts string to cls
    return instance.get(name = model_name)
    
def get_model_name(model): # converts cls to a string
    return instance.get_name(cls = model)

def get_model_name_list(): # converts cls to a string
    return instance.get_name_list()


def get_model_clean_name(model_name):
    return instance.clean_name(name = model_name)

# registry = {}
# 
# def register_model(cls):
#     class_name = cls.__name__
#     if registry.get(class_name) == None:
#         registry[class_name] = cls
#     else:
#         raise NameError('The class you are trying to register is already in!...')
#     
#     
# def get_model(model = None, model_name = None):
#     
#     if model == None and model_name == None:
#         raise AttributeError('you must specify a model_name')
#     
#     else:
#         model = model if model is not None else model_name
#     
#     model = registry.get(model) 
#     if model == None:
#         raise AttributeError('You have not properly registered this model name, or this name does not exist.')
#     
#     return model
# 
# 
# def get_model_name(model):
#     
#     model_name = model.__name__ if hasattr(model, "__name__") else model.__class__.__name__
#     
#     return model_name