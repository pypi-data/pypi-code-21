import json

class CloudExplorer(object):
    def __init__(self, parent):
        self.ci = parent.ci.cloud_explorer(parent.version)
        self.account_id = parent.account_id
    
    def get_supported_regions(self):
        """Get a list of supported AWS Regions

        https://console.cloudinsight.alertlogic.com/api/cloud_explorer/#api-Cloud_Explorer-GetSupportedRegions

        /cloud_explorer/v1/supported_regions"""
        resp = self.ci.supported_regions.GET()
        return resp.json()

    def get_role_policy(self, rule_set, account_id=None):
        """Get default AWS third-party role policy
        https://console.cloudinsight.alertlogic.com/api/cloud_explorer/#api-Cloud_Explorer-GetRolePolicy
        /cloud_explorer/v1/:account_id/policy/:rule_set
        """
        if not account_id:
            account_id = self.account_id
        resp = self.ci(account_id).policy(rule_set).GET()
        return resp.json()

    def discover(self, environment_id, path_args, account_id=None, **kwargs):
        """Initiate AWS environment discovery. Once the enviroment is discovered it becomes initialiazed and you may proceed with partial rediscovery requests. If you try to make partial redicover in case the enviroment is not yet initiliazed the whole environment will be discovered to become initialized. Normally a new created environment automatically begin its first discovery procedure.

        https://console.cloudinsight.alertlogic.com/api/cloud_explorer/#api-Cloud_Explorer-Discover

        /cloud_explorer/v1/:account_id/environments/:environment_id/discover[/:service_name[/:resource_type[/:resource_id]]]?:query_parameters

        Path_args: serice_name, resource_type, resource_id
        Params: region, filter, sync"""
        if not account_id:
            account_id = self.account_id
        rest = self.ci(account_id).environments(environment_id).discover
        if path_args:
            for arg in path_args:
                rest = rest(arg)
        resp = rest.POST(params=kwargs)
        return resp.ok

    def validate_exteral_credentials(self, rule_set, **data):
        """Validate External Environement Credentials
        
        https://console.cloudinsight.alertlogic.com/api/cloud_explorer/#api-Cloud_Explorer-ValidateExteralCredentials

        /cloud_explorer/v1/validate_credentials"""
        resp = self.ci.validate_credentials.POST(data=json.dumps(data), params={'rule_set': rule_set})
        return resp.ok

    def validate_stored_credentials(self, environment_id, account_id=None):
        """Validate Stored Environment Credentials

        https://console.cloudinsight.alertlogic.com/api/cloud_explorer/#api-Cloud_Explorer-ValidateStoredCredentials

        /cloud_explorer/v1/:account_id/environments/:environment_id/validate_credentials"""
        if not account_id:
            account_id = self.account_id
        resp = self.ci(account_id).environments(environment_id).validate_credentials.POST
        return resp.ok
