import boto3

from confluent_kafka import Producer
from django_cdc import settings

# initialize lambda function
lambda_client = None
kinesis_client = None
sns_client = None
sns_arn =None
kafka_producer_client=None

try:
    lambda_client = boto3.client(
        "lambda", region_name=settings.AWS_REGION_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    kinesis_client = boto3.client("kinesis", region_name=settings.AWS_REGION_NAME)

    kafka_producer_client = Producer(**settings.KAFKA_CONFIG)
    sns_client = boto3.client('sns')
    sns_arn = "{0}{1}{2}{3}{4}".format("arn:aws:sns:",settings.AWS_REGION_NAME,":",settings.RESOURCE_TYPE_FOR_SNS,":")
except:
    pass
