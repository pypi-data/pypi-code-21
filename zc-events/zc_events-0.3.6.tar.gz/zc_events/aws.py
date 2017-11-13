import sys
import uuid
import boto3
from botocore.exceptions import ClientError

from six import reraise as raise_

from django.conf import settings


class S3IOException(Exception):
    pass


def save_string_contents_to_s3(stringified_data, aws_bucket_name, content_key=None,
                               aws_access_key_id=None, aws_secret_access_key=None):
    """Save data (provided in string format) to S3 bucket and return s3 key."""

    aws_access_key_id = aws_access_key_id or settings.AWS_ACCESS_KEY_ID
    aws_secret_access_key = aws_secret_access_key or settings.AWS_SECRET_ACCESS_KEY

    try:
        if not content_key:
            content_key = str(uuid.uuid4())

        session = boto3.session.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        s3 = session.resource('s3')
        s3.Bucket(aws_bucket_name).put_object(Key=content_key, Body=stringified_data)
        return content_key
    except ClientError as error:
        msg = 'Failed to save contents to S3. aws_bucket_name: {}, content_key: {}, ' \
              'error_message: {}'.format(aws_bucket_name, content_key, error.message)
        raise_(S3IOException(msg), None, sys.exc_info()[2])


def save_file_contents_to_s3(filepath, aws_bucket_name, content_key=None,
                             aws_access_key_id=None, aws_secret_access_key=None):
    """Upload a local file to S3 bucket and return S3 key."""

    aws_access_key_id = aws_access_key_id or settings.AWS_ACCESS_KEY_ID
    aws_secret_access_key = aws_secret_access_key or settings.AWS_SECRET_ACCESS_KEY

    try:
        if not content_key:
            content_key = str(uuid.uuid4())

        session = boto3.session.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        s3 = session.resource('s3')
        s3.Bucket(aws_bucket_name).upload_file(filepath, content_key)
        return content_key
    except ClientError as error:
        msg = 'Failed to save contents to S3. filepath: {}, aws_bucket_name: {}, content_key: {}, ' \
              'error_message: {}'.format(filepath, aws_bucket_name, content_key, error.message)
        raise_(S3IOException(msg), None, sys.exc_info()[2])


def read_s3_file_as_string(aws_bucket_name, content_key, delete=False,
                           aws_access_key_id=None, aws_secret_access_key=None):
    """Get the contents of an S3 file as string and optionally delete the file from the bucket."""

    aws_access_key_id = aws_access_key_id or settings.AWS_ACCESS_KEY_ID
    aws_secret_access_key = aws_secret_access_key or settings.AWS_SECRET_ACCESS_KEY

    try:
        session = boto3.session.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        s3 = session.resource('s3')
        obj = s3.Object(aws_bucket_name, content_key).get()
        ouput = obj['Body'].read()

        if delete:
            obj.delete()

        return output
    except ClientError as error:
        msg = 'Failed to save contents to S3. aws_bucket_name: {}, content_key: {}, delete: {}, ' \
              'error_message: {}'.format(aws_bucket_name, content_key, delete, error.message)
        raise_(S3IOException(msg), None, sys.exc_info()[2])
