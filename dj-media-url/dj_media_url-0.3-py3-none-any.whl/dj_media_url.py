import logging

import urlobject

logger = logging.getLogger(__name__)


def get_path_from_file_url(url):
    if url.hostname == '.':
        return str(url.path)[1:]
    if url.hostname is None:
        return str(url.path)
    raise ValueError("File URL must be in the form file:///absolute-path "
                     "or file://./relative-path")


TRUE_STRINGS = ('true', 't', 'yes', 'y')
FALSE_STRINGS = ('false', 'f', 'no', 'n')


def cast_bool(value):
    v = value.lower()
    if v in TRUE_STRINGS:
        return True
    if v in FALSE_STRINGS:
        return False
    raise ValueError("{} is not valid, expected one of {} or {}".format(
        v, ', '.join(TRUE_STRINGS), ', '.join(FALSE_STRINGS),
    ))


def media_url(url_string):
    url = urlobject.URLObject(url_string)
    if url.scheme == 'file':
        return {
            'MEDIA_ROOT': get_path_from_file_url(url),
            'MEDIA_URL': url.query.dict.get('url', '/media/'),
        }

    if url.scheme in ('s3', 's3-insecure'):
        settings = {
            'DEFAULT_FILE_STORAGE': 'storages.backends.s3boto3.'
                                    'S3Boto3Storage',
            'AWS_ACCESS_KEY_ID': url.username,
            'AWS_SECRET_ACCESS_KEY': url.password,
            'AWS_STORAGE_BUCKET_NAME': url.path.segments[0],
            'AWS_S3_LOCATION': '/'.join(url.path.segments[1:]),
            'AWS_S3_USE_SSL': url.scheme == 's3',
        }
        if 'default-acl' in url.query.dict:
            settings['AWS_DEFAULT_ACL'] = url.query.dict['default-acl']
        if 'querystring-auth' in url.query.dict:
            settings['AWS_QUERYSTRING_AUTH'] = cast_bool(
                url.query.dict['querystring-auth'])
        if 'querystring-expire' in url.query.dict:
            settings['AWS_QUERYSTRING_EXPIRE'] = int(
                url.query.dict['querystring-expire'])
        if 'overwrite' in url.query.dict:
            settings['AWS_S3_FILE_OVERWRITE'] = cast_bool(
                url.query.dict['overwrite'])
        if url.hostname:
            settings['AWS_S3_HOST'] = url.hostname
        if 'region' in url.query.dict:
            settings['AWS_S3_REGION_NAME'] = url.query.dict['region']
        if 'domain' in url.query.dict:
            settings['AWS_S3_CUSTOM_DOMAIN'] = url.query.dict['custom-domain']
        return settings

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


EMAIL_BACKENDS = {
    'smtp': 'django.core.mail.backends.smtp.EmailBackend',
    'smtp-insecure': 'django.core.mail.backends.smtp.EmailBackend',
    'smtps': 'django.core.mail.backends.smtp.EmailBackend',
    'console': 'django.core.mail.backends.console.EmailBackend',
}
EMAIL_DEFAULT_PORTS = {
    'smtp': 587,
    'smtp-insecure': 25,
    'smtps': 465,
    'console': None,
}


def email_url(url_string, from_address=None):
    url = urlobject.URLObject(url_string)
    return (
        # EMAIL_BACKEND
        EMAIL_BACKENDS[url.scheme],
        # EMAIL_HOST
        url.hostname,
        # EMAIL_PORT
        url.port or EMAIL_DEFAULT_PORTS[url.scheme],
        # EMAIL_HOST_USER
        url.username,
        # EMAIL_HOST_PASSWORD
        url.password,
        # EMAIL_USE_TLS
        url.scheme == 'smtp',
        # EMAIL_USE_SSL
        url.scheme == 'smtps',
        # EMAIL_FROM_ADDRESS
        from_address or url.path.segments[0],
    )
