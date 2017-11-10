# -*- coding: utf-8 -*-

from dbaas_credentials.credential import Credential
from dbaas_credentials.models import CredentialType


class DatabaseAsAServiceApi(object):
    def __init__(self, databaseinfra):
        self.databaseinfra = databaseinfra

        integration = CredentialType.objects.get(
            type=CredentialType.NETWORKAPI
        )
        environment = self.databaseinfra.environment
        self.credentials = Credential.get_credentials(
            environment=environment, integration=integration
        )

    @property
    def user(self):
        return self.credentials.user

    @property
    def password(self):
        return self.credentials.password

    @property
    def endpoint(self):
        return self.credentials.endpoint

    @property
    def key(self):
        return self.credentials.secret

    @property
    def env_vip_id(self):
        return self.credentials.get_parameter_by_name('env_vip_id')

    @property
    def env_pool_id(self):
        return self.credentials.get_parameter_by_name('env_pool_id')

    @property
    def finality(self):
        return self.credentials.get_parameter_by_name('finality')

    @property
    def business(self):
        return self.credentials.get_parameter_by_name('business')

    @property
    def environment_vip(self):
        return int(self.env_vip_id)

    @property
    def cache_group(self):
        return int(self.credentials.get_parameter_by_name('cache_group'))

    @property
    def persistence(self):
        return int(self.credentials.get_parameter_by_name('persistence'))

    @property
    def timeout(self):
        return int(self.credentials.get_parameter_by_name('timeout'))

    @property
    def traffic_return(self):
        return int(self.credentials.get_parameter_by_name('traffic_return'))

    @property
    def l4_protocol(self):
        return int(self.credentials.get_parameter_by_name('l4_protocol'))

    @property
    def l7_protocol(self):
        return int(self.credentials.get_parameter_by_name('l7_protocol'))

    @property
    def l7_rule(self):
        return int(self.credentials.get_parameter_by_name('l7_rule'))

    @property
    def environment_pool(self):
        return int(self.env_pool_id)

    @property
    def lb_method(self):
        return self.credentials.get_parameter_by_name('lb_method')

    @property
    def priority(self):
        return int(self.credentials.get_parameter_by_name('priority'))

    @property
    def limit(self):
        return int(self.credentials.get_parameter_by_name('limit'))

    @property
    def member_status(self):
        return int(self.credentials.get_parameter_by_name('member_status'))

    @property
    def weight(self):
        return int(self.credentials.get_parameter_by_name('weight'))

    @property
    def servicedownaction(self):
        return {
            'name': self.credentials.get_parameter_by_name('servicedownaction')
        }

    @property
    def healthcheck_type(self):
        return self.credentials.get_parameter_by_name('healthcheck_type')

    @property
    def healthcheck_request(self):
        return self.credentials.get_parameter_by_name('healthcheck_request')

    @property
    def destination(self):
        return self.credentials.get_parameter_by_name('destination')

    @property
    def healthcheck_expect(self):
        return self.credentials.get_parameter_by_name('healthcheck_expect')

    @property
    def vm_name(self):
        return self.credentials.get_parameter_by_name('vm_name')
