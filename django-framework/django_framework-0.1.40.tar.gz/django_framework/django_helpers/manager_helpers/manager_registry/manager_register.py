from django_framework.django_helpers.register_helpers import Registry

instance = None
class ManagerRegistry(Registry):
    REGISTRY_TYPE = 'Manager'
    REGISTER = {}
    
    @classmethod
    def set_instance(cls):
        if instance == None:
            global instance
            instance = ManagerRegistry()


def register_manager(cls):
    ManagerRegistry.set_instance()
    instance.register(cls = cls)
    

def get_manager(manager_name): # converts string to cls
    return instance.get(name = manager_name)
    
def get_manager_name(manager): # converts cls to a string
    return instance.get_name(cls = manager)

def get_manager_name_list(): # converts cls to a string
    return instance.get_name_list()



