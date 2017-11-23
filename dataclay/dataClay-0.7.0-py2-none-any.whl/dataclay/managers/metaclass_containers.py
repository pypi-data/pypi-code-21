"""Management of dataClay MetaClass containers.

Note that this is NOT for Python "metaclass", but for the MetaClass container
which includes information of registered classes.

Take into account that managing MetaClass container tends to be a job for the
ExecutionEnvironment, not for the client. But with notable exceptions (like the
class registration, however it doesn't use those functions at the moment).

It is in the library instead of inside dclay_server because the ExecutionGateway
requires some specific methods from here. But this may change in the future.
"""

from dataclay import runtime
from dataclay.core.management import MetaClass
from dataclay.conf import settings
import lru
import os.path
import yaml

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


# FIXME un-hardcode this
cached_metaclasses = lru.LRU(200)
cached_metaclass_info = lru.LRU(200)


def deploy_metaclass(namespace, class_name, binary_data, metaclass_container):
    """Deploy binary data into the internal structure (currently, a file)
    :param namespace: The name of the namespace for the class.
    :param class_name: Name of the class.
    :param binary_data: Binary data, typically a MetaClass serialized.
    :param metaclass_container: The MetaClass container, typically equivalent
    to the previous binary data.

    Note that there is redundancy on the parameters because this is typically
    called after a server-side call to deployment, and thus the info is
    available in multiple form.
    """
    namespace_path = os.path.join(settings.deploy_path, namespace)
    if not os.access(namespace_path, os.X_OK | os.W_OK):
        # Assume that it is not created yet
        os.makedirs(namespace_path)
        if not os.access(namespace_path, os.X_OK | os.W_OK):
            raise OSError("Could not create/have write access to folder {}".
                          format(namespace_path))

    # Store in a file
    with open(os.path.join(namespace_path, class_name + ".mcs"), 'wb') as f:
        f.write(binary_data)

    if settings.cache_on_deploy:
        cached_metaclasses[class_name] = metaclass_container
        
def deploy_metaclass_grpc(namespace, class_name, metaclass_yaml_str, metaclass):
    """Deploy binary data into the internal structure (currently, a file)
    :param namespace: The name of the namespace for the class.
    :param class_name: Name of the class.
    :param metaclass: a MetaClass as YAML string.

    Note that there is redundancy on the parameters because this is typically
    called after a server-side call to deployment, and thus the info is
    available in multiple form.
    """
    namespace_path = os.path.join(settings.deploy_path, namespace)
    if not os.access(namespace_path, os.X_OK | os.W_OK):
        # Assume that it is not created yet
        os.makedirs(namespace_path)
        if not os.access(namespace_path, os.X_OK | os.W_OK):
            raise OSError("Could not create/have write access to folder {}".
                          format(namespace_path))

    # Store in a file
    with open(os.path.join(namespace_path, class_name + ".mcs"), 'wb') as f:
        f.write(metaclass_yaml_str)

    if settings.cache_on_deploy:
        cached_metaclasses[class_name] = metaclass


def load_metaclass(namespace, class_name):
    """Load binary data into a MetaClass container.
    :param namespace: The name of the namespace for the class.
    :param class_name: Name of the class.
    :return: A MetaClass container, deserialized from previously deployed binary data.
    """
    try:
        return cached_metaclasses[class_name]
    except KeyError:
        namespace_path = os.path.join(settings.deploy_path, namespace)
        with open(os.path.join(namespace_path, class_name + ".mcs"), 'rb') as f:
            mc_f = MetaClass.read(f)
            mc = yaml.load(mc_f)
        cached_metaclasses[class_name] = mc
        return mc


def load_metaclass_info(metaclass_id):
    """Load the namespace and class name for a certain MetaClassID.
    :param metaclass_id: The dataClay UUID of the MetaClass.
    :return: A tuple (class_name, namespace).
    """
    # FIXME this RPC will change and the classname will contain the namespace
    try:
        return cached_metaclass_info[metaclass_id]
    except KeyError:
        class_name, namespace = runtime.ready_clients["@LM"].get_classname_and_namespace_for_ds(metaclass_id)
        cached_metaclass_info[metaclass_id] = (class_name, namespace)
        return class_name, namespace
