# -*- encoding: utf-8 -*-

import json

import boto3
from botocore.exceptions import ClientError
import dateutil.parser


def is_object(bucket, key):
    """
    Checks if an object exists in S3.  Returns True/False.

    :param bucket: Bucket of the object to check.
    :param key: Key of the object to check.

    """
    client = boto3.client('s3')
    try:
        client.head_object(Bucket=bucket, Key=key)
    except ClientError as err:
        if err.response['Error']['Code'] == '404':
            return False
        else:
            raise
    else:
        return True


def copy_object(src_bucket, src_key, dst_bucket, dst_key, lazy=False):
    """
    Copy an object from one S3 bucket to another.

    :param src_bucket: Bucket of the source object.
    :param src_key: Key of the source object.
    :param dst_bucket: Bucket of the destination object.
    :param dst_key: Key of the destination object.
    :param lazy: Do a lazy copy.  This means that the object will only be
        copied if the destination object does not exist, or exists but has
        a different ETag from the source object.

    """
    client = boto3.client('s3')
    if not is_object(bucket=src_bucket, key=src_key):
        raise ValueError(
            f'Tried to copy missing object ({src_bucket}, {src_key})'
        )

    def should_copy():
        if not lazy:
            return True

        if not is_object(bucket=dst_bucket, key=dst_key):
            return True

        src_resp = client.head_object(Bucket=src_bucket, Key=src_key)
        dst_resp = client.head_object(Bucket=dst_bucket, Key=dst_key)
        return src_resp['ETag'] == dst_resp['ETag']

    if should_copy():
        return client.copy_object(
            CopySource={'Bucket': src_bucket, 'Key': src_key},
            Bucket=dst_bucket,
            Key=dst_key
        )


def _extract_s3_event(record):
    event_datetime = dateutil.parser.parse(record["eventTime"])

    return {
        "event_name": record["eventName"],
        "event_time": event_datetime,
        "bucket_name": record["s3"]["bucket"]["name"],
        "object_key": record["s3"]["object"]["key"],
        "size": record["s3"]["object"]["size"],
        "versionId": record["s3"]["object"].get("versionId")
    }


def parse_s3_record(event):
    """
    Extracts a simple subset of an S3 update event.
    """
    return [_extract_s3_event(record) for record in event["Records"]]


def write_objects_to_s3(bucket, key, objects):
    """
    Given an iterable of objects that can be serialised as JSON, serialise
    them as JSON, and write them to a file in S3, one per line.

    :param bucket: S3 bucket to upload the new file to.
    :param key: S3 key to upload the new file to.
    :param objects: An iterable of objects that can be serialised as JSON.

    """
    # We use sort_keys=True to ensure deterministic results.  The separators
    # flag allows us to write more compact JSON, which makes things faster!
    # See https://twitter.com/raymondh/status/842777864193769472
    json_str = b'\n'.join([
        json.dumps(m, sort_keys=True, separators=(',', ':')).encode('ascii')
        for m in objects
    ])

    client = boto3.client('s3')
    client.put_object(Bucket=bucket, Key=key, Body=json_str)


__all__ = [
    'is_object',
    'copy_object',
    'parse_s3_record',
    'write_objects_to_s3',
]
