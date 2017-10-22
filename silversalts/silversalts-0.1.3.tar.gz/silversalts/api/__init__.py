CURRENT_VERSION = '0.1.3'

def ocr(spec, user, secret, host='api.silversalts.com', protocol='https', **kwargs):
    import json
    import time
    import boto3
    import requests
    import botocore.exceptions

    from .crypter import SymmetricCrypter
    from .packager import SilverSaltsPackager


    def s3_file_exists(s3, bucket, key):
        exists = False
        try:
            s3.head_object(Bucket=bucket, Key=key)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                exists = False
            else:
                raise
        else:
            exists = True
        return exists


    url = '%s://%s/service/ocr' % (protocol, host, )
    spec.update(kwargs)
    spec['version'] = CURRENT_VERSION
    if isinstance(secret, str):
        ss_crypter = SymmetricCrypter()
    else:
        raise NotImplementedError('secret must be an ascii string')
    ss_packager = SilverSaltsPackager(ss_crypter)
    res = requests.post(
        url,
        headers={
            'user': user,
        },
        data=ss_packager.pack(spec, secret)
    )
    if res.status_code == 200:
        result = ss_packager.unpack(res.content, secret)
        if result['output_scheme'] == spec['output_scheme']:
            if result['input_scheme'] == 'raw':
                return result['data']
            elif result['input_scheme'] == 's3':
                desc = json.loads(result['data'])
                s3 = boto3.Session(desc['access'], desc['secret']).client("s3")
                for i in range(desc['retry'] + 1):
                    if s3_file_exists(s3, desc['bucket'], desc['key']):
                        return s3.get_object(
                            Bucket=desc['bucket'],
                            Key=desc['key']
                        )['Body'].read()
                    else:
                        time.sleep(desc['sleep'])
        raise ValueError('Something went very wrong, aborting ...')
    raise SystemError('Server went wrong: %s - %s' % (res.status_code, res.text, ))
