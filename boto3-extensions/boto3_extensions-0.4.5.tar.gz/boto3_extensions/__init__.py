import boto3
import logging
from logging import NullHandler
from botocore.credentials import RefreshableCredentials, create_assume_role_refresher, CredentialProvider
from boto3_extensions.exceptions import InvalidRoleArnException
from boto3_extensions.arn_patch import patch_session, \
                                   patch_service_context, \
                                   patch_resource_factory, \
                                   patch_resource_meta
from os import environ, path
from imp import reload

logging.getLogger(__name__).addHandler(NullHandler())
_logger = logging.getLogger(__name__)

dir_path = path.dirname(path.realpath(__file__))
environ['AWS_DATA_PATH'] = '{dir_path}/data/'.format(dir_path=dir_path)
reload(boto3)


def arn_patch_boto3():
    """
    Patch boto3 to support ARNs for all resources
    """
    patch_session()
    patch_service_context()
    patch_resource_factory()
    patch_resource_meta()
    _logger.info('Patched Boto3 with arn support')


class RefreshableAssumeRoleProvider(CredentialProvider):
    METHOD = 'iam-role'

    def __init__(self, role_arn=None, role_session_name=None, session=None):
        self._role_arn = role_arn
        self._role_session_name = role_session_name
        self._session=session
        self._sts_role_config = {"RoleArn": role_arn,
                                 "RoleSessionName": role_session_name}
    def load(self):
        client = self._session.client('sts') if self._session else boto3.client('sts')
        refresher = create_assume_role_refresher(client,
                                                 params=self._sts_role_config)
        metadata = refresher()
        if not metadata:
            return None
        _logger.debug('assumed credentials from IAM Role: %s',
                     self._role_arn)
        creds = RefreshableCredentials.create_from_metadata(
            metadata,
            method=self.METHOD,
            refresh_using=refresher
        )
        return creds


class ConnectionManager:
    '''
    Usage:
        connections = ConnectionManager(region_name='us-east-1')
        session = connections.get_session(role_arn='arn:aws:iam::1234567890:role/test-role', role_session_name='test')

    You can also provide a base session if you prefer:
        connections = ConnectionManager(session=my_boto3_session)

    '''
    def __init__(self, session=None, **kwargs):
        self._base_session = session
        self.default_session_args = kwargs
        self.connections = {}
    def get_session(self, role_arn, role_session_name):

        if (role_arn, role_session_name) not in self.connections:
            sts_role_config={"RoleArn": role_arn,
                "RoleSessionName": role_session_name}
            session = boto3.Session(**self.default_session_args)
            cred_provider = RefreshableAssumeRoleProvider(role_arn=role_arn,
                                                          role_session_name=role_session_name,
                                                          session=self._base_session)
            session._session \
                   .get_component('credential_provider') \
                   .providers \
                   .insert(0, cred_provider)
            self.connections[(role_arn, role_session_name)] = session
        return self.connections[(role_arn, role_session_name)]
