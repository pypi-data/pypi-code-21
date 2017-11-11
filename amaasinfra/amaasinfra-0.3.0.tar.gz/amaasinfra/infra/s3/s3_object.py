import boto3
import json

def get_object(bucket, key):
    s3 = boto3.client('s3')
    return s3.get_object(Bucket=bucket, Key=key)

def get_content(s3_object):
    return s3_object.get('Body').read().decode('utf-8')

def get_json_content(s3_object):
    return json.loads(get_content(s3_object))