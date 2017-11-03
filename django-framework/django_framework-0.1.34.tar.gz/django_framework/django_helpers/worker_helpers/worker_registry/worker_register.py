
instance = None

from django_framework.django_helpers.register_helpers import Registry

class WorkerRegistry(Registry):
    REGISTRY_TYPE = 'Worker'
    REGISTER = {}
    
    SHOULD_CHECK_TYPE = True
    
    @classmethod
    def set_instance(cls):
        if instance == None:
            global instance
            instance = WorkerRegistry()


def register_worker(cls):
    WorkerRegistry.set_instance()
    
    instance.register(cls = cls)

def get_worker(worker_name): # converts string to cls
    return instance.get(name = worker_name)
    
def get_worker_name(worker): # converts cls to a string
    return instance.get_name(cls = worker)

def get_worker_name_list(): # converts cls to a string
    return instance.get_name_list()


def get_worker_clean_name(worker_name):
    return instance.clean_name(name = worker_name)
