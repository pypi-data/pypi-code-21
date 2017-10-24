"""
Endpoint types.

"""
from os.path import abspath, exists, split

from microcosm_resourcesync.endpoints.directory_endpoint import DirectoryEndpoint
from microcosm_resourcesync.endpoints.http_endpoint import HTTPEndpoint
from microcosm_resourcesync.endpoints.null_endpoint import NullEndpoint
from microcosm_resourcesync.endpoints.pipe_endpoint import PipeEndpoint
from microcosm_resourcesync.endpoints.yaml_file_endpoint import YAMLFileEndpoint


def endpoint_for(endpoint):
    """
    Interpret endpoint as correct type.

    """
    if endpoint == "-":
        return PipeEndpoint()

    if endpoint == "null" or endpoint == "/dev/null":
        return NullEndpoint()

    if endpoint.startswith("http://") or endpoint.startswith("https://"):
        return HTTPEndpoint(endpoint)

    if endpoint.endswith(".yaml") or endpoint.endswith(".yml"):
        return YAMLFileEndpoint(endpoint)

    if exists(split(abspath(endpoint))[0]):
        return DirectoryEndpoint(endpoint)

    raise Exception
