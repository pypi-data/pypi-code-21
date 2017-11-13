"""This module allows securely storing and retrieving Twitter API
credentials in AWS EC2 System manager."""
import sys
import boto3

TWITTER_CREDENTIALS = {
    'consumer_key': {
        'Description': 'Twitter consumer key',
        'Type': 'String'
    },
    'consumer_secret': {
        'Description': 'Twitter consumer secret',
        'Type': 'SecureString'
    },
    'access_token': {
        'Description': 'Twitter access token',
        'Type': 'String'
    },
    'access_token_secret': {
        'Description': 'Twitter access token secret',
        'Type': 'SecureString'
    }
}
SSM_NAME_SEPARATOR = '.'

def retrieve_credentials(credential_namespace, aws_region=None,
                         aws_access_key_id=None, aws_secret_access_key=None):
    """Retrieves Twitter credentials from AWS EC2 System manager.

    The credentials are returned as a dict.
    They are decrypted before returning.
    Args:
        credential_namespace (string):
            Project name used as credential prefix.
        aws_region (string): AWS region name override

        The aws_* parameters are overrides passed to boto.

    Returns:
        dict: This function returns a dict with the following keys:
            * consumer_key
            * consumer_secret
            * access_token
            * access_token_secret
    """
    ssmname_to_key = _make_ssmname_to_key_map(credential_namespace)
    client = boto3.client('ssm', region_name=aws_region,
                          aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key)
    response = client.get_parameters(Names=list(ssmname_to_key.keys()),
                                     WithDecryption=True)
    responsedict = _credentials_response_to_dict(ssmname_to_key, response)
    if not responsedict:
        raise LookupError('No credentials found for namespace:' + credential_namespace)
    return responsedict

def upload_credentials(credential_namespace, credentials_dict, kms_key_id,
                       aws_region=None, aws_access_key_id=None,
                       aws_secret_access_key=None):
    """Save Twitter credentials securely into EC2 system manager.

    Credentials are retrieved from AWS EC2 System manager.
    They are decrypted before returning.
    Args:
        credential_namespace (string): Used as prefix for storing
            credentials.

        credentials_dict (dict): Twitter credentials dict.abs
            The dict should have the following inputs
            * consumer_key
            * consumer_secret
            * access_token
            * access_token_secret

        kms_key_id (string)

        aws_region (string): AWS region name override

        The aws_* parameters are optional overrides passed to boto.
        By default, boto library will read from env variables or
        ~/.aws/credentials
    """
    ssmname_to_key = _make_ssmname_to_key_map(credential_namespace)
    client = boto3.client(service_name='ssm', region_name=aws_region,
                          aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key)
    for ssmname, key in ssmname_to_key.items():
        credential_details = TWITTER_CREDENTIALS[key]
        description = credential_details['Description']
        param_type = credential_details['Type']
        key_id = kms_key_id if (param_type == 'SecureString') else None
        client.put_parameter(ssmname, description, credentials_dict[key],
                             param_type, key_id, True)

def _make_ssmname_to_key_map(credential_prefix):
    ssmname_to_key = {}
    for required_credential in TWITTER_CREDENTIALS:
        ssmname = credential_prefix + SSM_NAME_SEPARATOR + required_credential
        ssmname_to_key[ssmname] = required_credential
    return ssmname_to_key


def _credentials_response_to_dict(ssmname_to_key, response):
    responsedict = {}
    for credential in response['Parameters']:
        key = ssmname_to_key[credential['Name']]
        responsedict[key] = credential['Value']
    return responsedict
