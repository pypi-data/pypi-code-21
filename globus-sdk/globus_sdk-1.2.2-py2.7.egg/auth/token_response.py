import logging
import json
import requests
import time

from globus_sdk.response import GlobusHTTPResponse
from globus_sdk.exc import GlobusOptionalDependencyError

logger = logging.getLogger(__name__)


def _convert_token_info_dict(source_dict):
    """
    Extract a set of fields into a new dict for indexing by resource server.
    Allow for these fields to be `None` when absent:
        - "refresh_token"
        - "token_type"
    """
    expires_in = source_dict.get('expires_in', 0)

    return {
        'scope': source_dict['scope'],
        'access_token': source_dict['access_token'],
        'refresh_token': source_dict.get('refresh_token'),
        'token_type': source_dict.get('token_type'),
        'expires_at_seconds': int(time.time() + expires_in)
    }


class OAuthTokenResponse(GlobusHTTPResponse):
    """
    Class for responses from the OAuth2 code for tokens exchange used in
    3-legged OAuth flows.
    """
    def __init__(self, *args, **kwargs):
        GlobusHTTPResponse.__init__(self, *args, **kwargs)
        self._init_rs_dict()

    def _init_rs_dict(self):
        # call the helper at the top level
        self._by_resource_server = {
            self['resource_server']: _convert_token_info_dict(self)}
        # call the helper on everything in 'other_tokens'
        self._by_resource_server.update(dict(
            (unprocessed_item['resource_server'],
             _convert_token_info_dict(unprocessed_item))
            for unprocessed_item in self['other_tokens']))

    @property
    def by_resource_server(self):
        """
        Representation of the token response in a ``dict`` indexed by resource
        server.

        Although ``OAuthTokenResponse.data`` is still available and
        valid, this representation is typically more desirable for applications
        doing inspection of access tokens and refresh tokens.
        """
        return self._by_resource_server

    def decode_id_token(self, auth_client):
        """
        A parsed ID Token (OIDC) as a dict.
        """
        logger.info('Decoding ID Token "{}"'.format(self['id_token']))
        try:
            import jwt
        except ImportError:
            logger.error('OptionalDependencyError(jwt)')
            raise GlobusOptionalDependencyError(
                ["globus_sdk[jwt]"],
                "JWT Parsing via OAuthTokenResponse.id_token")

        logger.debug('Fetch JWK Data: Start')
        oidc_conf = auth_client.get('/.well-known/openid-configuration')
        jwks_uri = oidc_conf['jwks_uri']
        signing_algos = oidc_conf['id_token_signing_alg_values_supported']

        # use the auth_client's decision on ssl_verify=yes/no
        jwk_data = requests.get(jwks_uri, verify=auth_client._verify).json()
        logger.debug('Fetch JWK Data: Complete')
        # decode from JWK to an RSA PEM key for JWT decoding
        jwk_as_pem = jwt.algorithms.RSAAlgorithm.from_jwk(
            json.dumps(jwk_data['keys'][0]))

        return jwt.decode(
            self['id_token'], jwk_as_pem,
            algorithms=signing_algos, audience=auth_client.client_id)

    def __str__(self):
        # Make printing responses more convenient by only showing the
        # (typically important) token info
        return json.dumps(self.by_resource_server, indent=2)


class OAuthDependentTokenResponse(OAuthTokenResponse):
    """
    Class for responses from the OAuth2 code for tokens retrieved by the
    OAuth2 Dependent Token Extension Grant. For more complete docs, see
    :meth:`oauth2_get_dependent_tokens \
    <globus_sdk.ConfidentialAppAuthClient.oauth2_get_dependent_tokens>`
    """
    def _init_rs_dict(self):
        # call the helper on everything in the response array
        self._by_resource_server = dict(
            (unprocessed_item['resource_server'],
             _convert_token_info_dict(unprocessed_item))
            for unprocessed_item in self.data)

    def decode_id_token(self, auth_client):
        # just in case
        raise NotImplementedError(
            ('OAuthDependentTokenResponse.decode_id_token() is not and cannot '
             'be implemented. Dependent Tokens data does not include an '
             'id_token'))
