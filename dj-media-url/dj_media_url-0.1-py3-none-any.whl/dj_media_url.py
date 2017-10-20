import logging

import urlobject

logger = logging.getLogger(__name__)


def media_url(url_string):
    url = urlobject.URLObject(url_string)
    if url.scheme == 'file':
        return {
            'MEDIA_ROOT': url.path,
            'MEDIA_URL': url.query.dict.get('url', '/media/'),
        }
    if url.scheme in ('s3', 's3-insecure'):
        return {
            'DEFAULT_FILE_STORAGE': 'storages.backends.s3boto3.'
                                    'S3Boto3Storage',
            'AWS_ACCESS_KEY_ID': url.username,
            'AWS_SECRET_ACCESS_KEY': url.password,
            'AWS_STORAGE_BUCKET_NAME': url.path.segments[0],
            'AWS_DEFAULT_ACL': url.query.dict.get('default-acl', None),
            'AWS_QUERYSTRING_AUTH': 'querystring-auth' in url.query.dict,
            'AWS_QUERYSTRING_EXPIRE': url.query.dict.get(
                'querystring-expire', 3600
            ),
            'AWS_S3_FILE_OVERWRITE': 'no-overwrite' not in url.query.dict,
            'AWS_S3_HOST': url.hostname or 's3.amazonaws.com',
            'AWS_S3_LOCATION': '/'.join(url.path.segments[1:]),
            'AWS_S3_REGION_NAME': url.query.dict.get('region', None),
            'AWS_S3_USE_SSL': url.scheme == 's3',
            'AWS_S3_CUSTOM_DOMAIN': url.query.dict.get('custom-domain',
                                                       None),
        }
    if url.scheme == 'googlecloud':
        return {
            'DEFAULT_FILE_STORAGE': 'storages.backends.gcloud.'
                                    'GoogleCloudStorage',
            'GS_BUCKET_NAME': url.path.segments[0],
            'GS_PROJECT_ID': url.path.hostname,
            'GS_CREDENTIALS': url.username,
            'GS_FILE_OVERWRITE': 'no-overwrite' not in url.query.dict,
        }
    if url.scheme == 'azure':
        return {
            'DEFAULT_FILE_STORAGE': 'storages.backends.azure_storage.'
                                    'AzureStorage',
            'AZURE_ACCOUNT_NAME': url.username,
            'AZURE_ACCOUNT_KEY': url.password,
            'AZURE_CONTAINER': url.path.segments[0],
        }
