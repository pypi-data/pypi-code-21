class OpenStackClientsCls:

    def __init__(self, **kwargs):
        self._token = None
        self._keystoneclient = None
        self._novaclient = None
        self._neutronclient = None
        self._cinderclient = None
        self._glanceclient = None
        self._ceilometerclient = None

        self._credentials = kwargs
        if 'region_name' not in self._credentials:
            self._credentials['region_name'] = None

    @property
    def token(self):
        return self._token

    @token.getter
    def token(self):
        return self.keystone.auth_token

    @property
    def keystone(self):
        return self._keystoneclient

    @keystone.getter
    def keystone(self):
        if self._keystoneclient is None:
            from keystoneclient.v2_0 import client as KeystoneClient
            self._keystoneclient = KeystoneClient.Client(**self._credentials)
        return self._keystoneclient

    @property
    def neutron(self):
        return self._neutronclient

    @neutron.getter
    def neutron(self):
        if self._neutronclient is None:
            from neutronclient.v2_0 import client as NeutronClient

            endpoint = self.keystone.service_catalog.url_for(service_type='network', endpoint_type='publicURL')
            self._neutronclient = NeutronClient.Client(token=self.token, endpoint_url=endpoint, ca_cert=self._credentials['cacert'])

        return self._neutronclient

    @property
    def nova(self):
        return self._novaclient

    @neutron.getter
    def nova(self):
        if self._novaclient is None:
            from novaclient.client import Client as NovaClient

            self._novaclient = NovaClient('2', self._credentials['username'], self.token, self._credentials['tenant_name'], self._credentials['auth_url'], 'compute', auth_token=self.token, region_name=self._credentials['region_name'])

        return self._novaclient

    @property
    def cinder(self):
        return self._cinderclient

    @cinder.getter
    def cinder(self):
        if self._cinderclient is None:
            from cinderclient import client as CinderClient
            self._cinderclient = CinderClient.Client("2", self._credentials['username'], self._credentials['password'], self._credentials['tenant_name'], self._credentials['auth_url'], cacert=self._credentials['cacert'])

        return self._cinderclient

    @property
    def glance(self):
        return self._glanceclient

    @glance.getter
    def glance(self):
        if self._glanceclient is None:
            from glanceclient import client as GlanceClient
            endpoint = self.keystone.service_catalog.url_for(service_type='image', endpoint_type='publicURL')
            self._glanceclient = GlanceClient.Client('2', endpoint=endpoint, token=self.token, cacert=self._credentials['cacert'])

        return self._glanceclient

    @property
    def ceilometer(self):
        return self._ceilometerclient

    @ceilometer.getter
    def ceilometer(self):
        if self._ceilometerclient is None:
            from ceilometerclient import client as CeilometerClient
            endpoint = self.keystone.service_catalog.url_for(service_type='metering', endpoint_type='publicURL')
            self._ceilometerclient = CeilometerClient.get_client('2', os_token=self.token, os_endpoint=endpoint, cacert=self._credentials['cacert'])
        return self._ceilometerclient

# keep cache of all the clients for given input args


class OpenStackClientFactory:
    __key = []
    __value = []

    def get(self, **kwargs):
        for i, item in enumerate(self.__key):
            if cmp(item, kwargs) == 0:
                return self.__value[i]

        p = OpenStackClientsCls(**kwargs)
        self.__key.append(kwargs)
        self.__value.append(p)
        return p
