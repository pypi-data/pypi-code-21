# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.service_client import ServiceClient
from msrest import Serializer, Deserializer
from msrestazure import AzureConfiguration
from .version import VERSION
from .operations.backup_long_term_retention_policies_operations import BackupLongTermRetentionPoliciesOperations
from .operations.backup_long_term_retention_vaults_operations import BackupLongTermRetentionVaultsOperations
from .operations.restore_points_operations import RestorePointsOperations
from .operations.recoverable_databases_operations import RecoverableDatabasesOperations
from .operations.restorable_dropped_databases_operations import RestorableDroppedDatabasesOperations
from .operations.capabilities_operations import CapabilitiesOperations
from .operations.server_connection_policies_operations import ServerConnectionPoliciesOperations
from .operations.database_threat_detection_policies_operations import DatabaseThreatDetectionPoliciesOperations
from .operations.data_masking_policies_operations import DataMaskingPoliciesOperations
from .operations.data_masking_rules_operations import DataMaskingRulesOperations
from .operations.firewall_rules_operations import FirewallRulesOperations
from .operations.geo_backup_policies_operations import GeoBackupPoliciesOperations
from .operations.databases_operations import DatabasesOperations
from .operations.elastic_pools_operations import ElasticPoolsOperations
from .operations.replication_links_operations import ReplicationLinksOperations
from .operations.server_azure_ad_administrators_operations import ServerAzureADAdministratorsOperations
from .operations.server_communication_links_operations import ServerCommunicationLinksOperations
from .operations.service_objectives_operations import ServiceObjectivesOperations
from .operations.servers_operations import ServersOperations
from .operations.elastic_pool_activities_operations import ElasticPoolActivitiesOperations
from .operations.elastic_pool_database_activities_operations import ElasticPoolDatabaseActivitiesOperations
from .operations.recommended_elastic_pools_operations import RecommendedElasticPoolsOperations
from .operations.service_tier_advisors_operations import ServiceTierAdvisorsOperations
from .operations.transparent_data_encryptions_operations import TransparentDataEncryptionsOperations
from .operations.transparent_data_encryption_activities_operations import TransparentDataEncryptionActivitiesOperations
from .operations.server_usages_operations import ServerUsagesOperations
from .operations.database_usages_operations import DatabaseUsagesOperations
from .operations.database_blob_auditing_policies_operations import DatabaseBlobAuditingPoliciesOperations
from .operations.encryption_protectors_operations import EncryptionProtectorsOperations
from .operations.failover_groups_operations import FailoverGroupsOperations
from .operations.operations import Operations
from .operations.server_keys_operations import ServerKeysOperations
from .operations.sync_agents_operations import SyncAgentsOperations
from .operations.sync_groups_operations import SyncGroupsOperations
from .operations.sync_members_operations import SyncMembersOperations
from .operations.virtual_network_rules_operations import VirtualNetworkRulesOperations
from .operations.database_operations import DatabaseOperations
from . import models


class SqlManagementClientConfiguration(AzureConfiguration):
    """Configuration for SqlManagementClient
    Note that all parameters used to create this instance are saved as instance
    attributes.

    :param credentials: Credentials needed for the client to connect to Azure.
    :type credentials: :mod:`A msrestazure Credentials
     object<msrestazure.azure_active_directory>`
    :param subscription_id: The subscription ID that identifies an Azure
     subscription.
    :type subscription_id: str
    :param str base_url: Service URL
    """

    def __init__(
            self, credentials, subscription_id, base_url=None):

        if credentials is None:
            raise ValueError("Parameter 'credentials' must not be None.")
        if subscription_id is None:
            raise ValueError("Parameter 'subscription_id' must not be None.")
        if not base_url:
            base_url = 'https://management.azure.com'

        super(SqlManagementClientConfiguration, self).__init__(base_url)

        self.add_user_agent('sqlmanagementclient/{}'.format(VERSION))
        self.add_user_agent('Azure-SDK-For-Python')

        self.credentials = credentials
        self.subscription_id = subscription_id


class SqlManagementClient(object):
    """The Azure SQL Database management API provides a RESTful set of web services that interact with Azure SQL Database services to manage your databases. The API enables you to create, retrieve, update, and delete databases.

    :ivar config: Configuration for client.
    :vartype config: SqlManagementClientConfiguration

    :ivar backup_long_term_retention_policies: BackupLongTermRetentionPolicies operations
    :vartype backup_long_term_retention_policies: azure.mgmt.sql.operations.BackupLongTermRetentionPoliciesOperations
    :ivar backup_long_term_retention_vaults: BackupLongTermRetentionVaults operations
    :vartype backup_long_term_retention_vaults: azure.mgmt.sql.operations.BackupLongTermRetentionVaultsOperations
    :ivar restore_points: RestorePoints operations
    :vartype restore_points: azure.mgmt.sql.operations.RestorePointsOperations
    :ivar recoverable_databases: RecoverableDatabases operations
    :vartype recoverable_databases: azure.mgmt.sql.operations.RecoverableDatabasesOperations
    :ivar restorable_dropped_databases: RestorableDroppedDatabases operations
    :vartype restorable_dropped_databases: azure.mgmt.sql.operations.RestorableDroppedDatabasesOperations
    :ivar capabilities: Capabilities operations
    :vartype capabilities: azure.mgmt.sql.operations.CapabilitiesOperations
    :ivar server_connection_policies: ServerConnectionPolicies operations
    :vartype server_connection_policies: azure.mgmt.sql.operations.ServerConnectionPoliciesOperations
    :ivar database_threat_detection_policies: DatabaseThreatDetectionPolicies operations
    :vartype database_threat_detection_policies: azure.mgmt.sql.operations.DatabaseThreatDetectionPoliciesOperations
    :ivar data_masking_policies: DataMaskingPolicies operations
    :vartype data_masking_policies: azure.mgmt.sql.operations.DataMaskingPoliciesOperations
    :ivar data_masking_rules: DataMaskingRules operations
    :vartype data_masking_rules: azure.mgmt.sql.operations.DataMaskingRulesOperations
    :ivar firewall_rules: FirewallRules operations
    :vartype firewall_rules: azure.mgmt.sql.operations.FirewallRulesOperations
    :ivar geo_backup_policies: GeoBackupPolicies operations
    :vartype geo_backup_policies: azure.mgmt.sql.operations.GeoBackupPoliciesOperations
    :ivar databases: Databases operations
    :vartype databases: azure.mgmt.sql.operations.DatabasesOperations
    :ivar elastic_pools: ElasticPools operations
    :vartype elastic_pools: azure.mgmt.sql.operations.ElasticPoolsOperations
    :ivar replication_links: ReplicationLinks operations
    :vartype replication_links: azure.mgmt.sql.operations.ReplicationLinksOperations
    :ivar server_azure_ad_administrators: ServerAzureADAdministrators operations
    :vartype server_azure_ad_administrators: azure.mgmt.sql.operations.ServerAzureADAdministratorsOperations
    :ivar server_communication_links: ServerCommunicationLinks operations
    :vartype server_communication_links: azure.mgmt.sql.operations.ServerCommunicationLinksOperations
    :ivar service_objectives: ServiceObjectives operations
    :vartype service_objectives: azure.mgmt.sql.operations.ServiceObjectivesOperations
    :ivar servers: Servers operations
    :vartype servers: azure.mgmt.sql.operations.ServersOperations
    :ivar elastic_pool_activities: ElasticPoolActivities operations
    :vartype elastic_pool_activities: azure.mgmt.sql.operations.ElasticPoolActivitiesOperations
    :ivar elastic_pool_database_activities: ElasticPoolDatabaseActivities operations
    :vartype elastic_pool_database_activities: azure.mgmt.sql.operations.ElasticPoolDatabaseActivitiesOperations
    :ivar recommended_elastic_pools: RecommendedElasticPools operations
    :vartype recommended_elastic_pools: azure.mgmt.sql.operations.RecommendedElasticPoolsOperations
    :ivar service_tier_advisors: ServiceTierAdvisors operations
    :vartype service_tier_advisors: azure.mgmt.sql.operations.ServiceTierAdvisorsOperations
    :ivar transparent_data_encryptions: TransparentDataEncryptions operations
    :vartype transparent_data_encryptions: azure.mgmt.sql.operations.TransparentDataEncryptionsOperations
    :ivar transparent_data_encryption_activities: TransparentDataEncryptionActivities operations
    :vartype transparent_data_encryption_activities: azure.mgmt.sql.operations.TransparentDataEncryptionActivitiesOperations
    :ivar server_usages: ServerUsages operations
    :vartype server_usages: azure.mgmt.sql.operations.ServerUsagesOperations
    :ivar database_usages: DatabaseUsages operations
    :vartype database_usages: azure.mgmt.sql.operations.DatabaseUsagesOperations
    :ivar database_blob_auditing_policies: DatabaseBlobAuditingPolicies operations
    :vartype database_blob_auditing_policies: azure.mgmt.sql.operations.DatabaseBlobAuditingPoliciesOperations
    :ivar encryption_protectors: EncryptionProtectors operations
    :vartype encryption_protectors: azure.mgmt.sql.operations.EncryptionProtectorsOperations
    :ivar failover_groups: FailoverGroups operations
    :vartype failover_groups: azure.mgmt.sql.operations.FailoverGroupsOperations
    :ivar operations: Operations operations
    :vartype operations: azure.mgmt.sql.operations.Operations
    :ivar server_keys: ServerKeys operations
    :vartype server_keys: azure.mgmt.sql.operations.ServerKeysOperations
    :ivar sync_agents: SyncAgents operations
    :vartype sync_agents: azure.mgmt.sql.operations.SyncAgentsOperations
    :ivar sync_groups: SyncGroups operations
    :vartype sync_groups: azure.mgmt.sql.operations.SyncGroupsOperations
    :ivar sync_members: SyncMembers operations
    :vartype sync_members: azure.mgmt.sql.operations.SyncMembersOperations
    :ivar virtual_network_rules: VirtualNetworkRules operations
    :vartype virtual_network_rules: azure.mgmt.sql.operations.VirtualNetworkRulesOperations
    :ivar database_operations: DatabaseOperations operations
    :vartype database_operations: azure.mgmt.sql.operations.DatabaseOperations

    :param credentials: Credentials needed for the client to connect to Azure.
    :type credentials: :mod:`A msrestazure Credentials
     object<msrestazure.azure_active_directory>`
    :param subscription_id: The subscription ID that identifies an Azure
     subscription.
    :type subscription_id: str
    :param str base_url: Service URL
    """

    def __init__(
            self, credentials, subscription_id, base_url=None):

        self.config = SqlManagementClientConfiguration(credentials, subscription_id, base_url)
        self._client = ServiceClient(self.config.credentials, self.config)

        client_models = {k: v for k, v in models.__dict__.items() if isinstance(v, type)}
        self._serialize = Serializer(client_models)
        self._deserialize = Deserializer(client_models)

        self.backup_long_term_retention_policies = BackupLongTermRetentionPoliciesOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.backup_long_term_retention_vaults = BackupLongTermRetentionVaultsOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.restore_points = RestorePointsOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.recoverable_databases = RecoverableDatabasesOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.restorable_dropped_databases = RestorableDroppedDatabasesOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.capabilities = CapabilitiesOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.server_connection_policies = ServerConnectionPoliciesOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.database_threat_detection_policies = DatabaseThreatDetectionPoliciesOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.data_masking_policies = DataMaskingPoliciesOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.data_masking_rules = DataMaskingRulesOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.firewall_rules = FirewallRulesOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.geo_backup_policies = GeoBackupPoliciesOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.databases = DatabasesOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.elastic_pools = ElasticPoolsOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.replication_links = ReplicationLinksOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.server_azure_ad_administrators = ServerAzureADAdministratorsOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.server_communication_links = ServerCommunicationLinksOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.service_objectives = ServiceObjectivesOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.servers = ServersOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.elastic_pool_activities = ElasticPoolActivitiesOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.elastic_pool_database_activities = ElasticPoolDatabaseActivitiesOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.recommended_elastic_pools = RecommendedElasticPoolsOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.service_tier_advisors = ServiceTierAdvisorsOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.transparent_data_encryptions = TransparentDataEncryptionsOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.transparent_data_encryption_activities = TransparentDataEncryptionActivitiesOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.server_usages = ServerUsagesOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.database_usages = DatabaseUsagesOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.database_blob_auditing_policies = DatabaseBlobAuditingPoliciesOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.encryption_protectors = EncryptionProtectorsOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.failover_groups = FailoverGroupsOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.operations = Operations(
            self._client, self.config, self._serialize, self._deserialize)
        self.server_keys = ServerKeysOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.sync_agents = SyncAgentsOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.sync_groups = SyncGroupsOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.sync_members = SyncMembersOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.virtual_network_rules = VirtualNetworkRulesOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.database_operations = DatabaseOperations(
            self._client, self.config, self._serialize, self._deserialize)
