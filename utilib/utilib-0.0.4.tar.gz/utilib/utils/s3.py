from io import BytesIO
import aiobotocore
import mimetypes
import asyncio
import boto3


class S3Helper:

    def __init__(self, host, access_key, key_id, region='cn-north-1'):
        self.host = host
        self.aws_secret_access_key = access_key
        self.aws_access_key_id = key_id

        self.session = boto3.Session(
            aws_access_key_id=key_id,
            aws_secret_access_key=access_key,
            region_name=region
        )

    async def async_upload(self, bucket_name, filename, content):
        session = aiobotocore.get_session()
        content_type = mimetypes.guess_type(filename)[0]
        async with session.create_client(
            's3',
            region_name='cn-north-1',
            aws_secret_access_key=self.aws_secret_access_key,
            aws_access_key_id=self.aws_access_key_id
        ) as client:
            if content_type:
                await asyncio.get_event_loop().create_task(
                    client.put_object(
                        Bucket=bucket_name,
                        Key=filename,
                        Body=content,
                        ACL='public-read',
                        ContentType=content_type))
            else:
                await asyncio.get_event_loop().create_task(
                    client.put_object(
                        Bucket=bucket_name,
                        Key=filename,
                        Body=content,
                        ACL='public-read'))
            return 'https://%s/%s/%s' % (
                self.host,
                bucket_name,
                filename)

    async def async_download_fileobj(self, bucket_name, filename):
        session = aiobotocore.get_session()
        out = BytesIO()
        async with session.create_client(
            's3',
            region_name='cn-north-1',
            aws_secret_access_key=self.aws_secret_access_key,
            aws_access_key_id=self.aws_access_key_id
        ) as client:
            _response = await client.get_object(
                Bucket=bucket_name, Key=filename)
            async with _response['Body'] as stream:
                out.write(await stream.read())
                return out

    def upload(self, bucket_name, filename, content):
        content_type = mimetypes.guess_type(filename)[0]

        s3 = self.session.resource('s3')

        if content_type:
            s3.Bucket(bucket_name).put_object(
                Key=filename,
                Body=content,
                ContentType=content_type
                )
        else:
            s3.Bucket(bucket_name).put_object(
                Key=filename,
                Body=content
                )
        s3.meta.client._endpoint.http_session.close()
        return 'https://%s/%s/%s' % (self.host, bucket_name, filename)

    def download_fileobj(self, bucket_name, filename):
        out = BytesIO()
        s3 = self.session.resource('s3')
        s3.Bucket(bucket_name).download_fileobj(Key=filename, Fileobj=out)
        s3.meta.client._endpoint.http_session.close()
        return out
