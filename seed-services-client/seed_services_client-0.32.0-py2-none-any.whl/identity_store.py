from .seed_services import SeedServicesApiClient
from .utils import get_paginated_response


class IdentityStoreApiClient(SeedServicesApiClient):
    """
    Client for Identity Store Service.

    :param str auth_token:
        An access token.

    :param str api_url:
        The full URL of the API.

    :param JSONServiceClient session:
        An instance of JSONServiceClient to use

    """

    def __init__(self, auth_token, api_url, session=None, **kwargs):
        super(IdentityStoreApiClient, self).__init__(
            auth_token, api_url, session=session, **kwargs)

    def get_identities(self, params=None):
        return {"results": get_paginated_response(self.session, '/identities/',
                params=params)}

    def search_identities(self, field, value):
        # this is used for searching 'details' field to avoid DRF lacks
        # use "details__preferred_language" for example field
        params = {field: value}
        return {"results": get_paginated_response(self.session,
                '/identities/search/', params=params)}

    def get_identity(self, identity):
        # return None on 404 becuase that means an identity not found
        result = self.session.get('/identities/%s/' % identity,
                                  expected_response_codes=[404, 200])
        if "detail" in result and result["detail"] == "Not found.":
            return None
        return result

    def get_identity_by_address(self, address_type, address_value):
        params = {"details__addresses__%s" % address_type: address_value}
        return {"results": get_paginated_response(self.session,
                '/identities/search/', params=params)}

    def get_identity_address(self, identity_id, address_type='msisdn',
                             params=None):
        if params is None:
            params = {'default': True}

        response = self.session.get(
            '/identities/{0}/addresses/{1}'.format(identity_id, address_type),
            params=params)

        if len(response["results"]) > 0:
            return response["results"][0]["address"]
        else:
            return None

    def update_identity(self, identity, data=None):
        return self.session.patch('/identities/%s/' % identity, data=data)

    def create_identity(self, identity):
        return self.session.post('/identities/', data=identity)

    def get_optouts(self, params=None):
        return {"results": get_paginated_response(self.session,
                '/optouts/search/', params=params)}

    def create_optout(self, optout):
        return self.session.post('/optout/', data=optout)

    def create_optin(self, optin):
        return self.session.post('/optin/', data=optin)
