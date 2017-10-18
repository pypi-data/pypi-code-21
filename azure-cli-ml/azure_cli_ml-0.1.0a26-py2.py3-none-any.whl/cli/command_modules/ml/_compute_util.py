
from azure.cli.core.commands import client_factory
from azure.cli.core.util import CLIError
from ._constants import MLC_CLIENT_PATH
from ._constants import MLC_MODELS_PATH
from importlib import import_module
machine_learning_compute_management_client = import_module(MLC_CLIENT_PATH, package=__package__)
MachineLearningComputeManagementClient = machine_learning_compute_management_client.MachineLearningComputeManagementClient

mlc_models = import_module(MLC_MODELS_PATH, package=__package__)
OperationalizationCluster = mlc_models.OperationalizationCluster
ClusterType = mlc_models.ClusterType
AcsClusterProperties = mlc_models.AcsClusterProperties
KubernetesClusterProperties = mlc_models.KubernetesClusterProperties
ServicePrincipalProperties = mlc_models.ServicePrincipalProperties
ErrorResponseWrapperException = mlc_models.ErrorResponseWrapperException
AppInsightsCredentials = mlc_models.AppInsightsCredentials
GlobalServiceConfiguration = mlc_models.GlobalServiceConfiguration
SslConfiguration = mlc_models.SslConfiguration
StorageAccountProperties = mlc_models.StorageAccountProperties
ContainerRegistryProperties = mlc_models.ContainerRegistryProperties

from msrestazure.azure_exceptions import CloudError
from .commands import _handle_exceptions


def __get_client():
    return client_factory.get_mgmt_service_client(
        MachineLearningComputeManagementClient).operationalization_clusters


def get_compute_resource(resource_group, cluster_name):
    client = __get_client()
    cluster = client.get(resource_group, cluster_name)
    if cluster.provisioning_errors:
        try:
            error_details = cluster.provisioning_errors[0].error.details
            for detail in error_details:
                if detail.code != 'Ok' and 'exceeding quota limits' in detail.message:
                    detail.message = 'Resource quota limit exceeded.'
                    break
        except:
            cluster.provisioning_errors = None
    return serialize_operationalization_cluster(client, cluster)


def get_current_compute_resource(context):
    context.validate_active_and_compute_subscriptions()
    if (context.current_compute_resource_group is None or
        context.current_compute_name is None):
        raise CLIError('Resource group and compute name must be provided if current environment is unset.')

    try:
        return get_compute_resource(context.current_compute_resource_group,
                                    context.current_compute_name)
    except ErrorResponseWrapperException:
        context.unset_current_compute_and_warn_user()
        raise


def create_compute_resource(resource_group, cluster_name, cluster_type, sp_id, sp_pw,
                            location, agent_count, agent_vm_size, cert_str, key_str, ssl_enabled,
                            storage_arm_id, acr_arm_id, cert_cname, master_count):
    client = __get_client()
    orchestrator_type = 'Kubernetes'
    container_service = AcsClusterProperties(
        orchestrator_type=orchestrator_type,
        orchestrator_properties=KubernetesClusterProperties(
            service_principal=ServicePrincipalProperties(
                client_id=sp_id,
                secret=sp_pw
            )
        ),
        master_count=master_count
    )

    if agent_count:
        container_service.agent_count=agent_count

    if agent_vm_size:
        container_service.agent_vm_size=agent_vm_size

    oc = OperationalizationCluster(
        location=location,
        cluster_type=cluster_type,
        container_service=container_service,
        global_service_configuration=GlobalServiceConfiguration(
            ssl=SslConfiguration(
                status=ssl_enabled,
                cert=cert_str,
                key=key_str,
                cname=cert_cname,
            )
        ),
        storage_account=StorageAccountProperties(
            resource_id=storage_arm_id
        ),
        container_registry=ContainerRegistryProperties(
            resource_id=acr_arm_id
        )
    )
    if cluster_type == ClusterType.local:
        oc.container_service = None
    return client.create_or_update(resource_group, cluster_name, oc, raw=True).response


def delete_compute_resource(resource_group, cluster_name):
    client = __get_client()
    return client.delete(resource_group, cluster_name, raw=True).response


def get_compute_resource_keys(resource_group, cluster_name):
    try:
        client = __get_client()
        return client.list_keys(resource_group, cluster_name)
    except CloudError as exc:
        _handle_exceptions(exc)


def serialize_operationalization_cluster(compute_management_client, operationalization_cluster):
    serialized_cluster = {}
    for attr, key_type_map in operationalization_cluster._attribute_map.items():
        orig_attr = getattr(operationalization_cluster, attr)
        attr_type = key_type_map['type']
        serialized_cluster[attr] = compute_management_client._serialize._serialize(orig_attr, attr_type)
    cluster_details = operationalization_cluster.id.split('/')
    serialized_cluster['subscription'] = cluster_details[2]
    serialized_cluster['resource_group'] = cluster_details[4]
    serialized_cluster['current_execution_mode'] = 'local' if operationalization_cluster.cluster_type.lower() == ClusterType.local.value.lower() else 'cluster'

    return serialized_cluster
