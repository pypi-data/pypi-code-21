class Assets(object):
    def __init__(self, parent):
        self.ci = parent.ci.assets(parent.version)
        self.account_id = parent.account_id

    def asset_types_query(self, account_id=None):
        """The asset_types endpoint will return information about assets and relationships. It lists all the assets that can be used in the boolean query and declare asset group endpoints.

        https://console.cloudinsight.alertlogic.com/api/assets/#api-Assets_Queries-Asset_Types_Query

        /assets/v1/:account_id/asset_types"""
        if not account_id:
            account_id = self.account_id
        resp = self.ci(account_id).asset_types.GET()
        return resp.json()

    def general_query(self, environment_id, account_id=None, **params):
        """The assets interface returns objects of one or more asset types in rows of related objects. Only objects that have the requested set of relationships are returned. For example, asking for host,subnet,vpc will not return hosts that are not connected to a subnet.

        One row is returned for each unique combination of assets types in the query (in the asset_types parameter), so host,subnet,vpc will return one row per host, and tag,host,subnet,vpc will return one row per tag per host. Furthermore, the ordering of the requested asset types matters: there must be a relationship between nodes of consecutive types. So requesting asset types host,vpc,region will return different data than host,region,vpc.

        https://console.cloudinsight.alertlogic.com/api/assets/#api-Assets_Queries-General_Query

        /assets/v1/:account_id/environments/:environment_id/assets"""
        if not account_id:
            account_id = self.account_id
        resp = self.ci(account_id).environments(environment_id).assets.GET(params=params)
        return resp.json()

    def get_entire_environment_with_relationships(self, environment_id, account_id=None):
        """The endpoint returns all the assets and relationships for a single environment. Relationships are returned as a key value list where the key is a composite of both the assets keys.

        https://console.cloudinsight.alertlogic.com/api/assets/#api-Assets_Queries-Get_entire_environment_with_relationships

        /assets/v1/:account_id/export/:environment_id/relationships"""
        if not account_id:
            account_id = self.account_id
        resp = self.ci(account_id).environments(environment_id).relationships.GET()
        return resp.json()

    def remediations_query(self, environment_id, account_id=None, **params):
        """Remediations Query
        https://console.cloudinsight.alertlogic.com/api/assets/#api-Assets_Queries-Remediations_Query
        /assets/v1/:account_id/environments/:environment_id/remediations"""
        if not account_id:
            account_id = self.account_id
        resp = self.ci(account_id).environments(environment_id).remediations.GET(params=params)
        return resp.json()

    def topology_query(self, environment_id, account_id=None, **params):
        """Topology Query
        
        https://console.cloudinsight.alertlogic.com/api/assets/#api-Assets_Queries-Topology_Query

        /assets/v1/:account_id/environments/:environment_id/topology"""
        if not account_id:
            account_id = self.account_id
        resp = self.ci(account_id).environments(environment_id).topology.GET(params=params)
        return resp.json()

    def __declare_and_modify_assets(self, environment_id, account_id=None, **data):
        """ """
        if not account_id:
            account_id = self.account_id
        resp = self.ci(account_id).environments(environment_id).assets.PUT(data=json.dumps(data))
        return resp.json()

    def declare_access_levels(self, environment_id, account_id=None, **data):
        """Declare Access Levels

        https://console.cloudinsight.alertlogic.com/api/assets/#api-Declare_and_Modify-Declare_Access_Levels

        /assets/v1/:account_id/environments/:environment_id/assets"""
        return __declare_and_modify_assets(self, environment_id, account_id, **data)

    def declare_asset_group(self, environment_id, account_id=None, **data):
        """Declare Asset Group

        https://console.cloudinsight.alertlogic.com/api/assets/#api-Declare_and_Modify-Declare_Asset_Group

        /assets/v1/:account_id/environments/:environment_id/assets"""
        return __declare_and_modify_assets(self, environment_id, account_id, **data)

    def declare_assets(self, environment_id, account_id=None, **data):
        """Declare Assets

        https://console.cloudinsight.alertlogic.com/api/assets/#api-Declare_and_Modify-Declare_Assets

        /assets/v1/:account_id/environments/:environment_id/assets"""
        return __declare_and_modify_assets(self, environment_id, account_id, **data)

    def declare_batch(self, environment_id, account_id=None, **data):
        """Declare Batch

        https://console.cloudinsight.alertlogic.com/api/assets/#api-Declare_and_Modify-Declare_Batch

        /assets/v1/:account_id/environments/:environment_id/batch"""
        if not account_id:
            account_id = self.account_id
        resp = self.ci(account_id).environments(environment_id).batch.PUT(data=json.dumps(data))
        return resp.json()

    def declare_properties(self, environment_id, account_id=None, **data):
        """Declare Properties

        https://console.cloudinsight.alertlogic.com/api/assets/#api-Declare_and_Modify-Declare_Properties

        /assets/v1/:account_id/environments/:environment_id/assets"""
        return __declare_and_modify_assets(self, environment_id, account_id, **data)


    def declare_relationships(self, environment_id, account_id=None, **data):
        """Declare Relationships

        https://console.cloudinsight.alertlogic.com/api/assets/#api-Declare_and_Modify-Declare_Relationships

        /assets/v1/:account_id/environments/:environment_id/assets"""
        return __declare_and_modify_assets(self, environment_id, account_id, **data)

    def declare_vulnerabilities(self, environment_id, account_id=None, **data):
        """Declare Vulnerabilities
        
        https://console.cloudinsight.alertlogic.com/api/assets/#api-Declare_and_Modify-Declare_Vulnerabilities

        /assets/v1/:account_id/environments/:environment_id/assets"""
        return __declare_and_modify_assets(self, environment_id, account_id, **data)

    def remove_asset(self, environment_id, account_id=None, **data):
        """Remove Asset

        https://console.cloudinsight.alertlogic.com/api/assets/#api-Declare_and_Modify-Remove_Asset

        /assets/v1/:account_id/environments/:environment_id/assets"""
        return __declare_and_modify_assets(self, environment_id, account_id, **data)

    def remove_assets(self, environment_id, account_id=None, **data):
        """Remove Assets

        https://console.cloudinsight.alertlogic.com/api/assets/#api-Declare_and_Modify-Remove_Assets

        /assets/v1/:account_id/environments/:environment_id/assets"""
        return __declare_and_modify_assets(self, environment_id, account_id, **data)

    def remove_properties(self, environment_id, account_id=None, **data):
        """Remove Properties

        https://console.cloudinsight.alertlogic.com/api/assets/#api-Declare_and_Modify-Remove_Properties

        /assets/v1/:account_id/environments/:environment_id/assets"""
        return __declare_and_modify_assets(self, environment_id, account_id, **data)

    def remove_relationships(self, environment_id, account_id=None, **data):
        """Remove Relationships

        https://console.cloudinsight.alertlogic.com/api/assets/#api-Declare_and_Modify-Remove_Relationships

        /assets/v1/:account_id/environments/:environment_id/assets"""
        return __declare_and_modify_assets(self, environment_id, account_id, **data)

    def declare_environments(self, account_id=None, **data):
        """Declare Environments

        https://console.cloudinsight.alertlogic.com/api/assets/#api-Environments-Declare_Environments

        /assets/v1/:account_id/assets"""
        if not account_id:
            account_id = self.account_id
        resp = self.ci(account_id).assets.PUT(data=json.dumps(data))
        return resp.json()

    def get_environment(self, environment_id, account_id=None):
        """Get Environment

        https://console.cloudinsight.alertlogic.com/api/assets/#api-Environments-Get_Environment

        /assets/v1/:account_id/environments/:environment_id"""
        if not account_id:
            account_id = self.account_id
        resp = self.ci(account_id).environments(environment_id).GET()
        return resp.json()

    def list_environments(self, account_id=None):
        """List Environments

        https://console.cloudinsight.alertlogic.com/api/assets/#api-Environments-List_Environments

        /assets/v1/:account_id/environments"""
        if not account_id:
            account_id = self.account_id
        resp = self.ci(account_id).environments.GET()
        return resp.json()

    def complete_remediations(self, environment_id, account_id=None, **data):
        """Complete Remediations

        https://console.cloudinsight.alertlogic.com/api/assets/#api-Remediations-Complete_Remediations

        /assets/v1/:account_id/environments/:environment_id/assets"""
        return __declare_and_modify_assets(self, environment_id, account_id, **data)

    def dispose_remediations(self, environment_id, account_id=None, **data):
        """Dispose Remediations

        https://console.cloudinsight.alertlogic.com/api/assets/#api-Remediations-Dispose_Remediations

        /assets/v1/:account_id/environments/:environment_id/assets"""
        return __declare_and_modify_assets(self, environment_id, account_id, **data)

    def plan_remediations(self, environment_id, account_id=None, **data):
        """Plan Remediations

        https://console.cloudinsight.alertlogic.com/api/assets/#api-Remediations-Plan_Remediations

        /assets/v1/:account_id/environments/:environment_id/assets"""
        return __declare_and_modify_assets(self, environment_id, account_id, **data)

    def remediation_items_query(self, environment_id, account_id=None, **data):
        """Remediation Items Query

        https://console.cloudinsight.alertlogic.com/api/assets/#api-Remediations-Remediation_Items_Query

        /assets/v1/:account_id/environments/:environment_id/remediation-items"""
        if not account_id:
            account_id = self.account_id
        resp = self.ci(account_id).environments(environment_id)('remediation-items').GET()
        return resp.json()

    def uncomplete_remediations(self, environment_id, account_id=None, **data):
        """Uncomplete Remediations

        https://console.cloudinsight.alertlogic.com/api/assets/#api-Remediations-Uncomplete_Remediations

        /assets/v1/:account_id/environments/:environment_id/assets"""
        return __declare_and_modify_assets(self, environment_id, account_id, **data)

    def undispose_remediations(self, environment_id, account_id=None, **data):
        """Undispose Remediations
        https://console.cloudinsight.alertlogic.com/api/assets/#api-Remediations-Undispose_Remediations
        /assets/v1/:account_id/environments/:environment_id/assets"""
        return __declare_and_modify_assets(self, environment_id, account_id, **data)

    def boolean_query(self, environment_id, account_id=None, **data):
        """Special Queries - Boolean Query
        https://console.cloudinsight.alertlogic.com/api/assets/#api-Special_Queries-Boolean_Query
        /assets/v1/:account_id/environments/:environment_id/assets"""
        return __declare_and_modify_assets(self, environment_id, account_id, **data)


    def internet_accessible_hosts(self, environment_id, account_id=None):
        """Special Queries - Internet-accessible hosts
        https://console.cloudinsight.alertlogic.com/api/assets/#api-Special_Queries-Internet_Accessible_Hosts
        /assets/v1/:account_id/environments/:environment_id/hosts/internet-accessible"""
        if not account_id:
            account_id = self.account_id
        resp = self.ci(account_id).environments(environment_id).hosts('internet-accessible').GET()
        return resp.json()
